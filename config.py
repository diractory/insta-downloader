import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

API_ID   = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN not set! Add it in Render Environment tab.")

OWNER_USERNAMES   = ["Youradhey", "sunradhey"]
OWNER_IDS         = [int(x) for x in os.environ.get("OWNER_IDS", "").split(",") if x.strip().isdigit()]
SUDO_USERS        = [int(x) for x in os.environ.get("SUDO_USERS", "").split(",") if x.strip().isdigit()]
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "xivasudev")
BOT_NAME          = os.environ.get("BOT_NAME", "Radhey Downloader")
DOWNLOAD_DIR      = os.environ.get("DOWNLOAD_DIR", "downloads")
DATABASE_FILE     = os.environ.get("DATABASE_FILE", "radhey_bot.db")
PORT              = int(os.environ.get("PORT", "8080"))

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
