from pyrogram.errors import UserNotParticipant, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNEL
from utils.helpers import bold

async def is_subscribed(client, user_id):
    if not FORCE_SUB_CHANNEL: return True
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status not in ("left", "kicked", "banned")
    except UserNotParticipant:
        return False
    except RPCError:
        return True

def join_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
        [InlineKeyboardButton("✅ I've Joined — Try Again", callback_data="check_sub")],
    ])

def join_text():
    return bold(f"🔒 You must join @{FORCE_SUB_CHANNEL} to use this bot!\n\nJoin and press ✅ I've Joined.")
