"""
#RADHEY — Configuration
------------------------
Every setting the bot needs, pulled from environment variables so nothing
sensitive is hardcoded when you deploy (Render, VPS, Railway, etc).

For local testing you can create a `.env` file (see .env.example) and it
will be loaded automatically.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ── Telegram credentials ──────────────────────────────────────────────
# Pyrogram (unlike python-telegram-bot) needs an API_ID + API_HASH from
# https://my.telegram.org even when only running as a BOT.
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# BOT_TOKEN must come from an environment variable — never hardcode a real
# token here, especially in a public repo. Get yours from @BotFather and
# set it as BOT_TOKEN in your .env (local) or Render's Environment tab.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise SystemExit(
        "❌ BOT_TOKEN is not set!\n"
        "Set it as an environment variable (locally in .env, or in Render's "
        "Environment tab) — get a token from @BotFather on Telegram."
    )

# ── Owner / Admins ─────────────────────────────────────────────────────
OWNER_USERNAMES = ["Youradhey", "sunradhey"]
OWNER_IDS = [int(x) for x in os.environ.get("OWNER_IDS", "").split(",") if x.strip().isdigit()]
SUDO_USERS = [int(x) for x in os.environ.get("SUDO_USERS", "").split(",") if x.strip().isdigit()]

# ── Force Subscribe ────────────────────────────────────────────────────
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "xivasudev")  # without @

# ── Misc ───────────────────────────────────────────────────────────────
BOT_NAME = os.environ.get("BOT_NAME", "Radhey Downloader")
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")
DATABASE_FILE = os.environ.get("DATABASE_FILE", "radhey_bot.db")
PORT = int(os.environ.get("PORT", "8080"))  # Render provides this automatically

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
