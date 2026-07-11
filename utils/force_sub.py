"""
#RADHEY — Force Subscribe
--------------------------
Before a user can use the bot in DM, they must join @xivasudev (configurable
via FORCE_SUB_CHANNEL in config.py). This module exposes a single async
helper `is_subscribed()` plus a ready-made "please join" message + button
that every entry-point plugin (start, downloader) checks against.
"""

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, RPCError

from config import FORCE_SUB_CHANNEL
from utils.helpers import bold


async def is_subscribed(client: Client, user_id: int) -> bool:
    if not FORCE_SUB_CHANNEL:
        return True
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status not in ("left", "kicked", "banned")
    except UserNotParticipant:
        return False
    except ChatAdminRequired:
        # Bot isn't admin in the force-sub channel — fail open so the bot
        # doesn't lock everyone out because of a misconfiguration.
        print("[FORCE_SUB] Bot is not admin in the force-sub channel!")
        return True
    except RPCError as e:
        print(f"[FORCE_SUB] Error checking membership: {e}")
        return True


def join_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
            [InlineKeyboardButton("✅ I've Joined — Try Again", callback_data="check_sub")],
        ]
    )


def join_text() -> str:
    return bold(
        f"🔒 Access Restricted!\n\n"
        f"To use this bot you must first join our official channel: @{FORCE_SUB_CHANNEL}\n\n"
        f"Tap the button below to join, then press ✅ I've Joined."
    )
