"""
#RADHEY — Flask Web Server
---------------------------
Render (and similar PaaS hosts) requires "Web Service" deployments to
bind to a port. This tiny Flask app does that, serves the bot's landing
page (web/index.html), and exposes a JSON /health endpoint. It runs in a
background thread while the actual Telegram bot runs in the main thread.
"""

import os
import time
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="web", static_url_path="")
START_TIME = time.time()


@app.route("/")
def index():
    return send_from_directory("web", "index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "online",
            "uptime_seconds": int(time.time() - START_TIME),
            "bot": "Radhey Downloader",
            "owner": ["@Youradhey", "@sunradhey"],
            "tag": "#RADHEY",
        }
    )


def run_web_server(port: int):
    app.run(host="0.0.0.0", port=port)
