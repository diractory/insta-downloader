"""
#RADHEY — Broadcast Plugin
---------------------------
Owner/sudo-only. Reply to any message with /broadcast to copy it to every
user who has ever started the bot, or /gbroadcast to copy it to every
group the bot is in.
"""

import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

from utils.helpers import bold
from utils import db
from config import OWNER_IDS, SUDO_USERS


def _is_owner(user_id: int) -> bool:
    return user_id in (OWNER_IDS + SUDO_USERS)


@Client.on_message(filters.command("broadcast"))
async def broadcast_cmd(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        await message.reply_text(bold("🚫 This command is owner-only."), quote=True)
        return
    if not message.reply_to_message:
        await message.reply_text(bold("⚠️ Reply to the message you want to broadcast to all users."), quote=True)
        return

    users = db.all_users()
    status = await message.reply_text(bold(f"📢 Broadcasting to {len(users)} users..."), quote=True)

    sent, failed = 0, 0
    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except RPCError:
            failed += 1
        await asyncio.sleep(0.05)  # gentle throttle to avoid flood limits

    await status.edit_text(bold(f"✅ Broadcast complete!\n\nSent: {sent}\nFailed: {failed}"))


@Client.on_message(filters.command("gbroadcast"))
async def gbroadcast_cmd(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        await message.reply_text(bold("🚫 This command is owner-only."), quote=True)
        return
    if not message.reply_to_message:
        await message.reply_text(bold("⚠️ Reply to the message you want to broadcast to all groups."), quote=True)
        return

    chats = db.all_chats()
    status = await message.reply_text(bold(f"📢 Broadcasting to {len(chats)} groups..."), quote=True)

    sent, failed = 0, 0
    for cid in chats:
        try:
            await message.reply_to_message.copy(cid)
            sent += 1
        except RPCError:
            failed += 1
        await asyncio.sleep(0.05)

    await status.edit_text(bold(f"✅ Group broadcast complete!\n\nSent: {sent}\nFailed: {failed}"))
