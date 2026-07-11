"""
#RADHEY — Misc Commands
------------------------
/help, /id, /ping, /info, /stats
"""

import time

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from utils.helpers import bold, esc
from utils import db
from config import OWNER_IDS, SUDO_USERS

HELP_TEXT = bold(
    "📖 Command List\n\n"
    "──────── 📥 Downloader ────────\n"
    "• Just send any Instagram reel / post / video link in DM or group.\n"
    "• /dl [link] — force download a link\n\n"
    "──────── 👮 Group Admin (bot must be admin) ────────\n"
    "• /mute [reply/username] — mute a member\n"
    "• /unmute [reply/username] — unmute a member\n"
    "• /ban [reply/username] — ban a member\n"
    "• /unban [reply/username] — unban a member\n"
    "• /kick [reply/username] — kick a member\n"
    "• /promote [reply/username] — make admin\n"
    "• /demote [reply/username] — remove admin\n"
    "• /pin — pin the replied message\n"
    "• /unpin — unpin the replied message\n"
    "• /purge — delete messages from replied msg to now\n"
    "• /warn [reply/username] — warn a member (3 warns = auto ban)\n"
    "• /resetwarn [reply/username] — reset warnings\n"
    "• /info [reply/username] — get user info\n\n"
    "──────── 🛠 General ────────\n"
    "• /start — start the bot\n"
    "• /help — this message\n"
    "• /id — get chat/user id\n"
    "• /ping — check bot response time\n\n"
    "──────── 👑 Owner Only ────────\n"
    "• /broadcast [reply] — broadcast to all users\n"
    "• /gbroadcast [reply] — broadcast to all groups\n"
    "• /stats — bot usage stats\n\n"
    "#RADHEY"
)


@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(HELP_TEXT, quote=True)


@Client.on_callback_query(filters.regex("^show_help$"))
async def help_cb(client: Client, cq: CallbackQuery):
    await cq.answer()
    await cq.message.reply_text(HELP_TEXT, quote=True)


@Client.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start = time.time()
    sent = await message.reply_text(bold("🏓 Pinging..."), quote=True)
    delay = (time.time() - start) * 1000
    await sent.edit_text(bold(f"🏓 Pong! {delay:.2f} ms"))


@Client.on_message(filters.command("id"))
async def id_cmd(client: Client, message: Message):
    chat = message.chat
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    text = bold(
        f"💬 Chat ID: {chat.id}\n"
        f"👤 {'Replied User' if message.reply_to_message else 'Your'} ID: {target.id if target else 'N/A'}"
    )
    await message.reply_text(text, quote=True)


@Client.on_message(filters.command("info"))
async def info_cmd(client: Client, message: Message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    if not target:
        await message.reply_text(bold("⚠️ Couldn't find that user."), quote=True)
        return

    text = bold(
        f"👤 User Info\n\n"
        f"🆔 ID: {target.id}\n"
        f"📛 Name: {esc(target.first_name)} {esc(target.last_name or '')}\n"
        f"🔗 Username: @{target.username if target.username else 'none'}\n"
        f"🤖 Is Bot: {target.is_bot}\n"
        f"⭐ Is Premium: {getattr(target, 'is_premium', False)}"
    )
    try:
        photos = await client.get_chat_photos(target.id)
        photo = photos[0] if photos else None
    except Exception:
        photo = None

    if photo:
        await message.reply_photo(photo.file_id, caption=text, quote=True)
    else:
        await message.reply_text(text, quote=True)


@Client.on_message(filters.command("stats"))
async def stats_cmd(client: Client, message: Message):
    if message.from_user.id not in (OWNER_IDS + SUDO_USERS):
        await message.reply_text(bold("🚫 This command is owner-only."), quote=True)
        return
    users, chats = db.stats()
    text = bold(f"📊 Bot Stats\n\n👤 Total Users: {users}\n👥 Total Groups: {chats}\n\n#RADHEY")
    await message.reply_text(text, quote=True)
