import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import bold, esc
from utils.force_sub import is_subscribed, join_markup, join_text
from utils import db
from config import BOT_NAME, FORCE_SUB_CHANNEL

START_TIME = time.time()

def _menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Updates", url=f"https://t.me/{FORCE_SUB_CHANNEL}"),
         InlineKeyboardButton("📖 Help", callback_data="show_help")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/Youradhey")],
    ])

def register(app):

    @app.on_message(filters.command("start"))
    async def start_cmd(client, message):
        user = message.from_user
        if not user: return
        db.add_user(user.id, user.username or "", user.first_name or "")
        if message.chat.type != "private":
            db.add_chat(message.chat.id, message.chat.title or "")
            await message.reply_text(bold(f"👋 Hey {esc(user.first_name)}! I'm {BOT_NAME}.\nSend an Instagram link here and I'll download it!\nUse /help to see all commands."), quote=True)
            return

        subbed = await is_subscribed(client, user.id)
        if not subbed:
            await message.reply_text(join_text(), reply_markup=join_markup(), quote=True)
            return

        caption = bold(
            f"👋 Hey {esc(user.first_name)}!\n\n"
            f"Welcome to {BOT_NAME} 🎉\n\n"
            f"🆔 Your ID: <code>{user.id}</code>\n"
            f"🔗 Username: @{user.username if user.username else 'none'}\n"
            f"📛 Name: {esc(user.first_name)} {esc(user.last_name or '')}\n\n"
            f"📥 Send me any Instagram reel/post/video link and I'll download it!\n"
            f"👮 Add me as admin in your group for moderation commands.\n\n"
            f"Use /help to see everything I can do. #RADHEY"
        )
        try:
            photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
            photo = photos[0] if photos else None
        except Exception:
            photo = None

        if photo:
            await message.reply_photo(photo.file_id, caption=caption, reply_markup=_menu())
        else:
            await message.reply_text(caption, reply_markup=_menu())

    @app.on_callback_query(filters.regex("^check_sub$"))
    async def check_sub_cb(client, cq):
        subbed = await is_subscribed(client, cq.from_user.id)
        if subbed:
            await cq.answer("✅ Verified!", show_alert=True)
            await cq.message.delete()
        else:
            await cq.answer("❌ You still haven't joined!", show_alert=True)

    @app.on_callback_query(filters.regex("^show_help$"))
    async def help_cb(client, cq):
        await cq.answer()
        from plugins.misc import HELP_TEXT
        await cq.message.reply_text(HELP_TEXT, quote=True)
