import time
from pyrogram import filters
from utils.helpers import bold, esc
from utils import db
from config import OWNER_IDS, SUDO_USERS

HELP_TEXT = bold(
    "📖 Command List\n\n"
    "──── 📥 Downloader ────\n"
    "• Send any Instagram link → auto download\n"
    "• /dl [link] — force download\n\n"
    "──── 👮 Group Admin ────\n"
    "• /mute — mute a member\n"
    "• /unmute — unmute a member\n"
    "• /ban — ban a member\n"
    "• /unban — unban a member\n"
    "• /kick — kick a member\n"
    "• /promote — make admin\n"
    "• /demote — remove admin\n"
    "• /pin — pin replied message\n"
    "• /unpin — unpin message\n"
    "• /purge — delete messages\n"
    "• /warn — warn a member (3 = ban)\n"
    "• /resetwarn — reset warnings\n"
    "• /info — get user info\n\n"
    "──── General ────\n"
    "• /start — start the bot\n"
    "• /help — this message\n"
    "• /id — get your ID\n"
    "• /ping — check bot speed\n\n"
    "──── 👑 Owner Only ────\n"
    "• /broadcast — message all users\n"
    "• /gbroadcast — message all groups\n"
    "• /stats — bot stats\n\n"
    "#RADHEY"
)

def register(app):

    @app.on_message(filters.command("help"))
    async def help_cmd(client, message):
        await message.reply_text(HELP_TEXT, quote=True)

    @app.on_message(filters.command("ping"))
    async def ping_cmd(client, message):
        start = time.time()
        sent = await message.reply_text(bold("Pinging..."), quote=True)
        ms = (time.time() - start) * 1000
        await sent.edit_text(bold(f"Pong! {ms:.2f} ms"))

    @app.on_message(filters.command("id"))
    async def id_cmd(client, message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        text = bold(f"Chat ID: {message.chat.id}\nUser ID: {target.id if target else 'N/A'}")
        await message.reply_text(text, quote=True)

    @app.on_message(filters.command("info"))
    async def info_cmd(client, message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        if not target:
            await message.reply_text(bold("Could not find that user."), quote=True)
            return
        text = bold(
            f"User Info\n\n"
            f"ID: {target.id}\n"
            f"Name: {esc(target.first_name)} {esc(target.last_name or '')}\n"
            f"Username: @{target.username if target.username else 'none'}\n"
            f"Is Bot: {target.is_bot}"
        )
        await message.reply_text(text, quote=True)

    @app.on_message(filters.command("stats"))
    async def stats_cmd(client, message):
        if message.from_user.id not in (OWNER_IDS + SUDO_USERS):
            await message.reply_text(bold("Owner only."), quote=True)
            return
        u, c = db.stats()
        await message.reply_text(bold(f"Bot Stats\n\nUsers: {u}\nGroups: {c}\n\n#RADHEY"), quote=True)
