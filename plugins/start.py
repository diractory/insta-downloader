"""
#RADHEY — /start Plugin
------------------------
- Registers every user/chat into the DB (for broadcast + stats).
- Enforces force-subscribe before allowing DM usage.
- Shows the user their own Telegram info + profile picture on first start.
"""

import time

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME, FORCE_SUB_CHANNEL
from utils.helpers import bold, esc
from utils.force_sub import is_subscribed, join_markup, join_text
from utils import db

START_TIME = time.time()


def _main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("➕ Add me to your Group", url="https://t.me/"),
                InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}"),
            ],
            [
                InlineKeyboardButton("📖 Commands", callback_data="show_help"),
                InlineKeyboardButton("ℹ️ About", callback_data="show_about"),
            ],
            [InlineKeyboardButton("👑 Owners", url="https://t.me/Youradhey")],
        ]
    )


@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user = message.from_user
    if user is None:
        return

    db.add_user(user.id, user.username or "", user.first_name or "")
    if message.chat.type != "private":
        db.add_chat(message.chat.id, message.chat.title or "")

    # Force subscribe only applies in private chat
    if message.chat.type == "private":
        subbed = await is_subscribed(client, user.id)
        if not subbed:
            await message.reply_text(join_text(), reply_markup=join_markup(), quote=True)
            return

    mention = user.mention(style="html")
    caption = bold(
        f"👋 Hey {esc(user.first_name)}!\n\n"
        f"Welcome to {BOT_NAME} — your all-in-one Instagram downloader "
        f"AND group management assistant, all in one bot.\n\n"
        f"🆔 Your ID: {user.id}\n"
        f"🔗 Username: @{user.username if user.username else 'none'}\n"
        f"📛 Name: {esc(user.first_name)} {esc(user.last_name or '')}\n\n"
        f"📥 Send me any Instagram reel / post / video link and I'll download it for you.\n"
        f"👮 Add me as admin in your group to unlock moderation commands.\n\n"
        f"Use /help to see everything I can do."
    )

    try:
        photos = await client.get_chat_photos(user.id)
        photo = photos[0] if photos else None
    except Exception:
        photo = None

    if photo:
        await message.reply_photo(photo.file_id, caption=caption, reply_markup=_main_menu())
    else:
        await message.reply_text(caption, reply_markup=_main_menu())


@Client.on_callback_query(filters.regex("^check_sub$"))
async def check_sub_cb(client: Client, cq: CallbackQuery):
    subbed = await is_subscribed(client, cq.from_user.id)
    if subbed:
        await cq.answer("✅ Verified! You can use the bot now.", show_alert=True)
        await cq.message.delete()
        await start_cmd(client, cq.message)
    else:
        await cq.answer("❌ You still haven't joined the channel!", show_alert=True)


@Client.on_callback_query(filters.regex("^show_about$"))
async def about_cb(client: Client, cq: CallbackQuery):
    uptime = int(time.time() - START_TIME)
    h, rem = divmod(uptime, 3600)
    m, s = divmod(rem, 60)
    text = bold(
        f"ℹ️ About {BOT_NAME}\n\n"
        f"⚙️ Engine: Pyrogram (MTProto)\n"
        f"📦 Downloader: yt-dlp + instaloader\n"
        f"⏱️ Uptime: {h}h {m}m {s}s\n"
        f"👑 Owner: @Youradhey | @sunradhey\n"
        f"#RADHEY"
    )
    await cq.answer()
    await cq.message.reply_text(text, quote=True)
