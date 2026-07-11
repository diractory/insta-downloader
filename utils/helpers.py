"""
#RADHEY — Helper Utilities
---------------------------
Small shared helpers used across every plugin: bold-text formatting
(every bot message is sent bold, per spec), progress bar rendering,
instagram link detection, and byte/time formatting.
"""

import re
import html
import time

INSTAGRAM_REGEX = re.compile(
    r"(https?://(?:www\.)?instagram\.com/(?:reel|reels|p|tv|stories)/[^\s?#]+[^\s]*)",
    re.IGNORECASE,
)


def bold(text: str) -> str:
    """Wrap text in HTML bold tags. ALL bot text goes through this."""
    return f"<b>{text}</b>"


def esc(text: str) -> str:
    """Escape text that will be embedded inside an HTML-parsed message."""
    return html.escape(str(text))


def extract_instagram_links(text: str):
    if not text:
        return []
    return INSTAGRAM_REGEX.findall(text)


def human_size(num_bytes: float) -> str:
    if not num_bytes:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def progress_bar(percent: float, length: int = 14) -> str:
    percent = max(0.0, min(100.0, percent))
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percent:5.1f}%"


class Throttle:
    """Prevents flooding Telegram with too-frequent message edits."""

    def __init__(self, min_interval: float = 2.0):
        self.min_interval = min_interval
        self._last = 0.0

    def ready(self) -> bool:
        now = time.time()
        if now - self._last >= self.min_interval:
            self._last = now
            return True
        return False
