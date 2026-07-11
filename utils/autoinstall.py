"""
#RADHEY — Auto Dependency Installer
"""

import importlib
import subprocess
import sys

REQUIRED_PACKAGES = {
    "pyrogram": "pyrofork",
    "tgcrypto": "TgCrypto",
    "yt_dlp": "yt-dlp",
    "instaloader": "instaloader",
    "flask": "flask",
    "requests": "requests",
    "dotenv": "python-dotenv",
    "PIL": "Pillow",
}


def _pip_install(pip_name: str) -> bool:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", pip_name]
        )
        return True
    except Exception as e:
        print(f"[AUTOINSTALL] Could not install '{pip_name}': {e}")
        return False


def ensure_dependencies():
    print("[AUTOINSTALL] Checking dependencies... (#RADHEY)")
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            print(f"[AUTOINSTALL] '{module_name}' missing -> installing '{pip_name}' ...")
            if _pip_install(pip_name):
                try:
                    importlib.import_module(module_name)
                    print(f"[AUTOINSTALL] '{module_name}' installed OK.")
                except ImportError as e:
                    print(f"[AUTOINSTALL] WARNING: still not importable: {e}")
    print("[AUTOINSTALL] Done.\n")
