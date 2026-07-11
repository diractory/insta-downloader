
from utils.autoinstall import ensure_dependencies
ensure_dependencies()

import threading, logging, asyncio
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, PORT, BOT_NAME
from web_server import run_web_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("RADHEY")

def start_web():
    try: run_web_server(PORT)
    except Exception as e: log.warning(f"Web server error: {e}")

async def run_bot():
    app = Client(
        name="radhey_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )

    from plugins import start, downloader, admin, broadcast, misc
    start.register(app)
    downloader.register(app)
    admin.register(app)
    broadcast.register(app)
    misc.register(app)

    await app.start()
    me = await app.get_me()
    log.info(f"✅ Bot running as @{me.username} — #RADHEY")
    await idle()
    await app.stop()

def main():
    log.info(f"Booting {BOT_NAME}...")
    threading.Thread(target=start_web, daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot())
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down...")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
