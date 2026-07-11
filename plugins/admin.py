"""
#RADHEY — Group Management Plugin
----------------------------------
MissRose-style moderation commands. The BOT must be a group admin with
the relevant rights (restrict / ban / pin / delete members) for these to
work, and the PERSON issuing the command must themselves be a group admin
(or bot owner/sudo).
"""

import asyncio
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import RPCError, UserAdminInvalid, ChatAdminRequired

from utils.helpers import bold, esc
from utils import db
from config import OWNER_IDS, SUDO_USERS

GROUP_ONLY = filters.group


# ── Permission helpers ─────────────────────────────────────────────────
async def is_group_admin(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id in (OWNER_IDS + SUDO_USERS):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator", "owner")
    except RPCError:
        return False


async def bot_is_admin(client: Client, chat_id: int) -> bool:
    try:
        me = await client.get_me()
        member = await client.get_chat_member(chat_id, me.id)
        return member.status in ("administrator", "creator", "owner")
    except RPCError:
        return False


async def resolve_target(client: Client, message: Message):
    """Get the target user from a reply, or from @username / user_id argument."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user, message.command[1:]

    parts = message.command[1:]
    if not parts:
        return None, []

    ident = parts[0]
    try:
        user = await client.get_users(ident)
        return user, parts[1:]
    except Exception:
        return None, parts


async def _guard(client: Client, message: Message) -> bool:
    """Common checks shared by every admin command. Returns True if OK to proceed."""
    if message.chat.type == "private":
        await message.reply_text(bold("⚠️ This command only works in groups."), quote=True)
        return False
    if not await is_group_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text(bold("🚫 You must be a group admin to use this command."), quote=True)
        return False
    if not await bot_is_admin(client, message.chat.id):
        await message.reply_text(
            bold("🚫 I need to be an admin in this group (with ban/restrict rights) to do that."),
            quote=True,
        )
        return False
    return True


# ── MUTE / UNMUTE ──────────────────────────────────────────────────────
@Client.on_message(filters.command("mute") & GROUP_ONLY)
async def mute_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, args = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to mute."), quote=True)
        return
    try:
        await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions())
        await message.reply_text(bold(f"🔇 Muted {esc(target.first_name)} successfully."), quote=True)
    except (UserAdminInvalid, ChatAdminRequired):
        await message.reply_text(bold("🚫 I can't mute this user (they may be an admin)."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to mute: {esc(e)}"), quote=True)


@Client.on_message(filters.command("unmute") & GROUP_ONLY)
async def unmute_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to unmute."), quote=True)
        return
    try:
        await client.restrict_chat_member(
            message.chat.id,
            target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        await message.reply_text(bold(f"🔊 Unmuted {esc(target.first_name)} successfully."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to unmute: {esc(e)}"), quote=True)


# ── BAN / UNBAN / KICK ─────────────────────────────────────────────────
@Client.on_message(filters.command("ban") & GROUP_ONLY)
async def ban_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to ban."), quote=True)
        return
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await message.reply_text(bold(f"🔨 Banned {esc(target.first_name)} from the group."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to ban: {esc(e)}"), quote=True)


@Client.on_message(filters.command("unban") & GROUP_ONLY)
async def unban_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to unban."), quote=True)
        return
    try:
        await client.unban_chat_member(message.chat.id, target.id)
        await message.reply_text(bold(f"✅ Unbanned {esc(target.first_name)}."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to unban: {esc(e)}"), quote=True)


@Client.on_message(filters.command("kick") & GROUP_ONLY)
async def kick_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to kick."), quote=True)
        return
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)  # unban right after = kick, not ban
        await message.reply_text(bold(f"👢 Kicked {esc(target.first_name)} from the group."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to kick: {esc(e)}"), quote=True)


# ── PROMOTE / DEMOTE ───────────────────────────────────────────────────
@Client.on_message(filters.command("promote") & GROUP_ONLY)
async def promote_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to promote."), quote=True)
        return
    try:
        from pyrogram.types import ChatPrivileges
        await client.promote_chat_member(
            message.chat.id,
            target.id,
            privileges=ChatPrivileges(
                can_change_info=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_chat=True,
            ),
        )
        await message.reply_text(bold(f"⭐ Promoted {esc(target.first_name)} to admin."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to promote: {esc(e)}"), quote=True)


@Client.on_message(filters.command("demote") & GROUP_ONLY)
async def demote_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to demote."), quote=True)
        return
    try:
        from pyrogram.types import ChatPrivileges
        await client.promote_chat_member(message.chat.id, target.id, privileges=ChatPrivileges())
        await message.reply_text(bold(f"⬇️ Demoted {esc(target.first_name)}."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to demote: {esc(e)}"), quote=True)


# ── PIN / UNPIN ────────────────────────────────────────────────────────
@Client.on_message(filters.command("pin") & GROUP_ONLY)
async def pin_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    if not message.reply_to_message:
        await message.reply_text(bold("⚠️ Reply to the message you want to pin."), quote=True)
        return
    try:
        await message.reply_to_message.pin(disable_notification=True)
        await message.reply_text(bold("📌 Message pinned."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to pin: {esc(e)}"), quote=True)


@Client.on_message(filters.command("unpin") & GROUP_ONLY)
async def unpin_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    try:
        if message.reply_to_message:
            await message.reply_to_message.unpin()
        else:
            await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text(bold("📌 Message(s) unpinned."), quote=True)
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to unpin: {esc(e)}"), quote=True)


# ── PURGE ──────────────────────────────────────────────────────────────
@Client.on_message(filters.command("purge") & GROUP_ONLY)
async def purge_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    if not message.reply_to_message:
        await message.reply_text(bold("⚠️ Reply to the message you want to purge from."), quote=True)
        return
    start_id = message.reply_to_message.id
    end_id = message.id
    ids = list(range(start_id, end_id + 1))
    deleted = 0
    try:
        for i in range(0, len(ids), 100):
            chunk = ids[i:i + 100]
            await client.delete_messages(message.chat.id, chunk)
            deleted += len(chunk)
        note = await client.send_message(message.chat.id, bold(f"🧹 Purged {deleted} messages."))
        await asyncio.sleep(4)
        await note.delete()
    except RPCError as e:
        await message.reply_text(bold(f"❌ Failed to purge: {esc(e)}"), quote=True)


# ── WARN / RESETWARN ───────────────────────────────────────────────────
@Client.on_message(filters.command("warn") & GROUP_ONLY)
async def warn_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID to warn."), quote=True)
        return
    count = db.add_warn(message.chat.id, target.id)
    if count >= 3:
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            db.reset_warn(message.chat.id, target.id)
            await message.reply_text(
                bold(f"🔨 {esc(target.first_name)} reached 3 warnings and has been banned."), quote=True
            )
        except RPCError as e:
            await message.reply_text(bold(f"❌ Failed to auto-ban: {esc(e)}"), quote=True)
    else:
        await message.reply_text(
            bold(f"⚠️ Warned {esc(target.first_name)} ({count}/3)."), quote=True
        )


@Client.on_message(filters.command("resetwarn") & GROUP_ONLY)
async def resetwarn_cmd(client: Client, message: Message):
    if not await _guard(client, message):
        return
    target, _ = await resolve_target(client, message)
    if not target:
        await message.reply_text(bold("⚠️ Reply to a user or give a username/ID."), quote=True)
        return
    db.reset_warn(message.chat.id, target.id)
    await message.reply_text(bold(f"✅ Warnings reset for {esc(target.first_name)}."), quote=True)
