"""
#RADHEY — Instagram Downloader Plugin
---------------------------------------
Send any Instagram reel / post / video / IGTV link (DM or group) and the
bot downloads it, showing a live progress bar for both the download and
the Telegram upload, then delivers the media with an inline
"Show Caption" button.

Primary engine : yt-dlp        (handles reels/posts/igtv without login)
Fallback engine: instaloader   (used if yt-dlp can't resolve the post)
"""

import os
import re
import uuid
import asyncio
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import DOWNLOAD_DIR
from utils.helpers import bold, esc, human_size, progress_bar, Throttle, extract_instagram_links
from utils.force_sub import is_subscribed, join_markup, join_text
from utils import db

# short-lived in-memory store for captions (avoids the 64-byte callback_data limit)
CAPTION_STORE = {}
SHORTCODE_RE = re.compile(r"instagram\.com/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)")


def _caption_markup(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("📝 Show Caption", callback_data=f"cap_{token}")]])


async def _run_ytdlp(url: str, out_template: str, loop, status_msg, throttle: Throttle):
    import yt_dlp

    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes", 0)
            percent = (done / total * 100) if total else 0
            if throttle.ready():
                text = bold(
                    f"⬇️ Downloading...\n\n{progress_bar(percent)}\n"
                    f"{human_size(done)} / {human_size(total)}"
                )
                asyncio.run_coroutine_threadsafe(_safe_edit(status_msg, text), loop)
        elif d.get("status") == "finished":
            asyncio.run_coroutine_threadsafe(
                _safe_edit(status_msg, bold("⚙️ Processing downloaded file...")), loop
            )

    ydl_opts = {
        "outtmpl": out_template,
        "format": "best[ext=mp4]/best",
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            return filepath, info.get("description") or info.get("title") or ""

    return await loop.run_in_executor(None, _download)


async def _run_instaloader_fallback(url: str, out_dir: str):
    import instaloader
    import requests

    match = SHORTCODE_RE.search(url)
    if not match:
        raise ValueError("Could not parse Instagram shortcode from URL.")
    shortcode = match.group(1)

    L = instaloader.Instaloader(dirname_pattern=out_dir, save_metadata=False, download_comments=False)
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    media_url = post.video_url if post.is_video else post.url
    caption = post.caption or ""

    ext = "mp4" if post.is_video else "jpg"
    filepath = os.path.join(out_dir, f"{shortcode}.{ext}")

    resp = requests.get(media_url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)

    return filepath, caption


async def _safe_edit(msg: Message, text: str):
    try:
        await msg.edit_text(text)
    except Exception:
        pass


async def _upload_progress(current, total, status_msg, throttle: Throttle):
    if throttle.ready() or current == total:
        percent = (current / total * 100) if total else 0
        text = bold(f"⬆️ Uploading to Telegram...\n\n{progress_bar(percent)}\n{human_size(current)} / {human_size(total)}")
        await _safe_edit(status_msg, text)


async def process_instagram_link(client: Client, message: Message, url: str):
    status = await message.reply_text(bold("🔍 Fetching your Instagram link..."), quote=True)
    loop = asyncio.get_event_loop()
    throttle = Throttle(min_interval=2.5)

    job_id = uuid.uuid4().hex[:10]
    out_dir = os.path.join(DOWNLOAD_DIR, job_id)
    os.makedirs(out_dir, exist_ok=True)
    out_template = os.path.join(out_dir, "%(id)s.%(ext)s")

    filepath = None
    caption = ""

    try:
        try:
            filepath, caption = await _run_ytdlp(url, out_template, loop, status, throttle)
        except Exception as primary_err:
            await _safe_edit(status, bold("♻️ Primary engine failed, trying fallback engine..."))
            filepath, caption = await _run_instaloader_fallback(url, out_dir)

        if not filepath or not os.path.exists(filepath):
            raise RuntimeError("Download finished but the output file is missing.")

        token = uuid.uuid4().hex[:12]
        CAPTION_STORE[token] = caption.strip() if caption else "No caption found for this post."

        await _safe_edit(status, bold("⬆️ Starting upload to Telegram..."))
        upload_throttle = Throttle(min_interval=2.5)

        is_video = filepath.lower().endswith((".mp4", ".mov", ".mkv", ".webm"))
        common_kwargs = dict(
            chat_id=message.chat.id,
            reply_to_message_id=message.id,
            reply_markup=_caption_markup(token),
            progress=lambda cur, tot: _upload_progress(cur, tot, status, upload_throttle),
        )

        if is_video:
            await client.send_video(video=filepath, supports_streaming=True, **common_kwargs)
        else:
            await client.send_photo(photo=filepath, **common_kwargs)

        await status.delete()

    except Exception as e:
        traceback.print_exc()
        await _safe_edit(
            status,
            bold(
                "❌ Sorry, I couldn't download that link.\n\n"
                "This can happen if the post is private, age-restricted, or a login-only story.\n"
                f"Error: {esc(str(e))[:200]}"
            ),
        )
    finally:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            if os.path.isdir(out_dir) and not os.listdir(out_dir):
                os.rmdir(out_dir)
        except Exception:
            pass


@Client.on_message((filters.private | filters.group) & filters.text & ~filters.command(["dl"]))
async def link_listener(client: Client, message: Message):
    if not message.text or message.text.startswith("/"):
        return
    links = extract_instagram_links(message.text)
    if not links:
        return

    if message.chat.type == "private":
        subbed = await is_subscribed(client, message.from_user.id)
        if not subbed:
            await message.reply_text(join_text(), reply_markup=join_markup(), quote=True)
            return

    for link in links[:3]:  # cap at 3 links per message to avoid abuse/flood
        await process_instagram_link(client, message, link)


@Client.on_message(filters.command("dl"))
async def dl_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(bold("⚠️ Usage: /dl <instagram link>"), quote=True)
        return
    url = message.command[1]
    if message.chat.type == "private":
        subbed = await is_subscribed(client, message.from_user.id)
        if not subbed:
            await message.reply_text(join_text(), reply_markup=join_markup(), quote=True)
            return
    await process_instagram_link(client, message, url)


@Client.on_callback_query(filters.regex(r"^cap_"))
async def show_caption_cb(client: Client, cq: CallbackQuery):
    token = cq.data.split("_", 1)[1]
    caption = CAPTION_STORE.get(token, "Caption no longer available.")
    if len(caption) > 900:
        caption = caption[:900] + "…"
    await cq.answer()
    await cq.message.reply_text(bold(f"📝 Caption:\n\n{esc(caption)}"), quote=True)
