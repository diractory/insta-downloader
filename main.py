"""
#RADHEY — Main Entry Point
"""

from utils.autoinstall import ensure_dependencies
ensure_dependencies()

import threading
import logging
import asyncio

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, PORT, BOT_NAME
from web_server import run_web_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("RADHEY")


def start_web_server():
    try:
        run_web_server(PORT)
    except Exception as e:
        log.warning(f"Web server failed to start: {e}")


async def run_bot():
    app = Client(
        name="radhey_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins"),
    )
    await app.start()
    log.info("Bot is running! #RADHEY")
    await asyncio.Event().wait()  # run forever


def main():
    log.info(f"Booting {BOT_NAME} — #RADHEY")

    # Flask in background thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    log.info(f"Web server started on port {PORT}")

    # Run bot with a fresh event loop — compatible with Python 3.10+, 3.14
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
