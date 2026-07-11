import os, uuid, asyncio, traceback
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DOWNLOAD_DIR
from utils.helpers import bold, esc, human_size, progress_bar, Throttle, extract_instagram_links
from utils.force_sub import is_subscribed, join_markup, join_text
from utils import db

CAPTION_STORE = {}

def _cap_btn(token):
    return InlineKeyboardMarkup([[InlineKeyboardButton("📝 Show Caption", callback_data=f"cap_{token}")]])

async def _safe_edit(msg, text):
    try: await msg.edit_text(text)
    except: pass

async def _ytdlp_download(url, out_tpl, loop, status, throttle):
    import yt_dlp
    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done  = d.get("downloaded_bytes", 0)
            pct   = (done/total*100) if total else 0
            if throttle.ready():
                text = bold(f"Downloading...\n\n{progress_bar(pct)}\n{human_size(done)} / {human_size(total)}")
                asyncio.run_coroutine_threadsafe(_safe_edit(status, text), loop)
    opts = {"outtmpl": out_tpl, "format": "best[ext=mp4]/best",
            "progress_hooks": [hook], "quiet": True, "noplaylist": True}
    def _dl():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info), info.get("description") or info.get("title") or ""
    return await loop.run_in_executor(None, _dl)

async def _instaloader_fallback(url, out_dir):
    import re, requests, instaloader
    sc = re.search(r"instagram\.com/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)", url)
    if not sc: raise ValueError("Could not parse shortcode.")
    L = instaloader.Instaloader(dirname_pattern=out_dir, save_metadata=False, download_comments=False)
    post = instaloader.Post.from_shortcode(L.context, sc.group(1))
    media_url = post.video_url if post.is_video else post.url
    ext = "mp4" if post.is_video else "jpg"
    fp = os.path.join(out_dir, f"{sc.group(1)}.{ext}")
    r = requests.get(media_url, stream=True, timeout=60); r.raise_for_status()
    with open(fp, "wb") as f:
        for chunk in r.iter_content(1024*256):
            if chunk: f.write(chunk)
    return fp, post.caption or ""

async def process_link(client, message, url):
    status = await message.reply_text(bold("Fetching your Instagram link..."), quote=True)
    loop   = asyncio.get_event_loop()
    thr    = Throttle(2.5)
    job_id = uuid.uuid4().hex[:10]
    out_dir = os.path.join(DOWNLOAD_DIR, job_id)
    os.makedirs(out_dir, exist_ok=True)
    filepath = caption = None
    try:
        try:
            filepath, caption = await _ytdlp_download(url, os.path.join(out_dir,"%(id)s.%(ext)s"), loop, status, thr)
        except Exception:
            await _safe_edit(status, bold("Trying fallback engine..."))
            filepath, caption = await _instaloader_fallback(url, out_dir)

        if not filepath or not os.path.exists(filepath):
            raise RuntimeError("Download finished but file is missing.")

        token = uuid.uuid4().hex[:12]
        CAPTION_STORE[token] = caption.strip() if caption else "No caption."

        await _safe_edit(status, bold("Uploading to Telegram..."))
        up_thr = Throttle(2.5)

        async def up_progress(cur, tot):
            if up_thr.ready() or cur == tot:
                pct = (cur/tot*100) if tot else 0
                await _safe_edit(status, bold(f"Uploading...\n\n{progress_bar(pct)}\n{human_size(cur)} / {human_size(tot)}"))

        is_video = filepath.lower().endswith((".mp4",".mov",".mkv",".webm"))
        kw = dict(chat_id=message.chat.id, reply_to_message_id=message.id,
                  reply_markup=_cap_btn(token), progress=up_progress)
        if is_video:
            await client.send_video(video=filepath, supports_streaming=True, **kw)
        else:
            await client.send_photo(photo=filepath, **kw)
        await status.delete()
    except Exception as e:
        traceback.print_exc()
        await _safe_edit(status, bold(f"Failed to download.\n\nThis happens with private posts or stories.\nError: {esc(str(e))[:200]}"))
    finally:
        try:
            if filepath and os.path.exists(filepath): os.remove(filepath)
            if os.path.isdir(out_dir) and not os.listdir(out_dir): os.rmdir(out_dir)
        except: pass

def register(app):

    @app.on_message((filters.private | filters.group) & filters.text)
    async def link_listener(client, message):
        if not message.text or message.text.startswith("/"): return
        links = extract_instagram_links(message.text)
        if not links: return
        if message.chat.type == "private":
            if not await is_subscribed(client, message.from_user.id):
                await message.reply_text(join_text(), reply_markup=join_markup(), quote=True); return
        for link in links[:3]:
            await process_link(client, message, link)

    @app.on_message(filters.command("dl"))
    async def dl_cmd(client, message):
        if len(message.command) < 2:
            await message.reply_text(bold("Usage: /dl <instagram link>"), quote=True); return
        if message.chat.type == "private":
            if not await is_subscribed(client, message.from_user.id):
                await message.reply_text(join_text(), reply_markup=join_markup(), quote=True); return
        await process_link(client, message, message.command[1])

    @app.on_callback_query(filters.regex(r"^cap_"))
    async def show_caption(client, cq):
        token = cq.data.split("_", 1)[1]
        cap = CAPTION_STORE.get(token, "Caption no longer available.")
        if len(cap) > 900: cap = cap[:900] + "…"
        await cq.answer()
        await cq.message.reply_text(bold(f"Caption:\n\n{esc(cap)}"), quote=True)
