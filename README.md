# 🤖 Radhey — Instagram Downloader & Group Guardian Bot

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Framework](https://img.shields.io/badge/Framework-Pyrogram-2AA9EE)](https://docs.pyrogram.org/)
[![Platform](https://img.shields.io/badge/Platform-Render%20%7C%20VPS%20%7C%20Termux-orange)]()
[![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen)]()

An all-in-one Telegram bot: instantly downloads Instagram reels/posts/videos
with a **live progress bar**, plus full **group management** (mute, ban,
unban, kick, promote, warn, purge, pin...) — built with **Pyrogram**,
**yt-dlp**, **instaloader**, and **Flask** (for hosting on Render).

**Owner:** [@Youradhey](https://t.me/Youradhey) · [@sunradhey](https://t.me/sunradhey)

---

## 📚 Table of Contents

- [Features](#-features)
- [Use Cases](#-use-cases)
- [Installation](#-installation)
  - [Termux Setup](#termux-android)
  - [Linux / Windows / Render Setup](#linux--windows--render)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Command Reference](#️-command-reference)
- [Notes & Limits](#️-notes--limits)
- [Developer](#-developer)
- [Support](#-support)

---

## ✨ Features

- 📥 **Instant downloads** — send any Instagram reel/post/video link (DM or group), auto-downloaded with a **live progress bar**
- 📝 **Show Caption button** — original post caption stays one tap away instead of cluttering the chat
- 🔒 **Force-subscribe gate** — users must join `@xivasudev` before using the bot in DM
- 👮 **Full group admin toolkit** — `/mute /unmute /ban /unban /kick /promote /demote /pin /unpin /purge /warn /resetwarn`
- 📢 **Owner broadcast tools** — `/broadcast`, `/gbroadcast`, `/stats`
- 🙋 **Rich /start** — shows the user their own Telegram info + profile picture
- 🧠 **Self-installing** — missing Python packages are auto pip-installed on first run, zero manual setup
- 🌐 **Bundled website** — polished `index.html` landing/status page served via Flask (Render-ready out of the box)
- 🔠 **Bold everywhere** — every single bot reply is sent in bold

---

## 💡 Use Cases

- **Content Saving** — grab reels/posts you want to keep or repost, with credit
- **Community Moderation** — run a group without babysitting it manually
- **Onboarding Funnels** — force-subscribe gate to grow your channel alongside the bot
- **Announcements** — broadcast updates to every user or group instantly

---

## 📦 Installation

### Termux (Android)

Copy and paste this entire block into Termux:

```bash
pkg install python git -y && git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git && cd YOUR_REPO && python main.py
```

That's it — the script installs its own Python dependencies and starts automatically.

### Linux / Windows / Render

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
cp .env.example .env      # then edit .env with your own values
python main.py
```

> No `pip install -r requirements.txt` step needed — the bot auto-installs anything missing the moment it boots. You can still run it up front if you prefer a faster first launch.

---

## ⚙️ Configuration

All configuration is done through environment variables — **never hardcode secrets into the code**, especially in a public repo.

| Variable | Required | Where to get it |
|---|---|---|
| `API_ID` | ✅ | [my.telegram.org](https://my.telegram.org) → API Development Tools |
| `API_HASH` | ✅ | same as above |
| `BOT_TOKEN` | ✅ | [@BotFather](https://t.me/BotFather) on Telegram |
| `OWNER_IDS` | ✅ | your numeric Telegram ID, from [@userinfobot](https://t.me/userinfobot) |
| `SUDO_USERS` | optional | comma-separated extra admin IDs |
| `FORCE_SUB_CHANNEL` | optional | channel username (no `@`) users must join, defaults to `xivasudev` |
| `PORT` | optional | set automatically by Render |

Copy `.env.example` → `.env` for local runs, or set these under **Render → your service → Environment** for deployment (see below).

### 🚀 Deploying on Render

1. Push this repo to your own GitHub (public or private, doesn't matter — secrets live in env vars, never in code)
2. On [Render](https://render.com) → **New +** → **Web Service** → connect the repo
3. Render auto-detects `render.yaml`. If not, set manually:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
4. Go to your service → **Environment** tab → **Add Environment Variable** → add each row from the table above (`API_ID`, `API_HASH`, `BOT_TOKEN`, `OWNER_IDS`, etc.) one at a time → **Save Changes**
5. Render redeploys automatically. It gives your service a `PORT` for free, which `web_server.py` binds to — that's what keeps the "Web Service" health check green while the Telegram bot runs alongside it in the same process.
6. Once live, add the bot to your group and **promote it to admin** (Ban users, Restrict members, Pin messages, Delete messages) to unlock the moderation commands.

---

## ▶️ Usage

Once the bot is running and added to a chat:

1. **In DM** — send `/start`, join the force-sub channel if prompted, then just paste any Instagram reel/post link. The bot replies with a live progress bar, then delivers the file with a **Show Caption** button.
2. **In a group** — anyone can paste a link the same way; no admin rights needed for downloads.
3. **For moderation** — promote the bot to admin in your group (see step 6 below), then any existing group admin can reply to a member's message with a command like `/mute`, `/ban`, or `/warn` — or type the command followed by `@username` / their numeric ID.
4. **As the owner** — reply to any message with `/broadcast` (all users) or `/gbroadcast` (all groups) to send it everywhere at once, or run `/stats` for usage numbers.

```bash
# quick sanity check after deploying — should reply instantly
/ping
```

---

## 🗒️ Command Reference

| Command | Where | Who | Description |
|---|---|---|---|
| `/start` | DM | Everyone | Start the bot, shows your info + PFP |
| `(paste an IG link)` | DM/Group | Everyone (after force-sub in DM) | Downloads the reel/post with a progress bar |
| `/dl <link>` | DM/Group | Everyone | Force-download a specific link |
| `/mute` `/unmute` | Group | Group Admins | Restrict / restore a member's ability to send messages |
| `/ban` `/unban` `/kick` | Group | Group Admins | Remove members |
| `/promote` `/demote` | Group | Group Admins | Manage admin rights |
| `/pin` `/unpin` | Group | Group Admins | Pin management |
| `/purge` | Group | Group Admins | Bulk-delete messages |
| `/warn` `/resetwarn` | Group | Group Admins | 3 warnings = auto-ban |
| `/id` `/info` `/ping` | Anywhere | Everyone | Utility commands |
| `/broadcast` `/gbroadcast` `/stats` | DM | Owner only | Message every user / every group, view stats |

---

## ⚠️ Notes & Limits

- Instagram **stories** and fully private accounts require a logged-in session and are not supported without extra setup (Instagram login is intentionally not baked in here to avoid risking your personal account).
- Be mindful of Telegram's flood limits when broadcasting to very large user counts — the bot throttles automatically, but very large lists take time.
- Respect Instagram's Terms of Service and content owners' rights when redistributing downloaded media.
- If you ever paste a real token/secret anywhere public (chat, repo, screenshot), treat it as compromised and regenerate it immediately via @BotFather.

---

## 👨‍💻 Developer

Project layout, for anyone extending the bot:

```
radhey-bot/
├── main.py                 # entry point — auto-installs deps, boots Flask + Pyrogram
├── config.py                # settings, all pulled from env vars
├── web_server.py             # Flask app (health check + serves index.html)
├── plugins/
│   ├── start.py                # /start, force-sub check, callbacks
│   ├── downloader.py             # Instagram download engine + progress bar
│   ├── admin.py                    # group moderation commands
│   ├── broadcast.py                 # owner broadcast tools
│   └── misc.py                       # /help /id /ping /info /stats
└── utils/
    ├── autoinstall.py                # auto pip-installs missing packages
    ├── db.py                          # sqlite storage (users/chats/warns)
    ├── helpers.py                      # progress bar, bold text, regex helpers
    └── force_sub.py                    # force-subscribe logic
```

Pyrogram auto-discovers every handler decorated with `@Client.on_message` /
`@Client.on_callback_query` inside `plugins/`, so adding a new command is as
simple as dropping a new file (or function) in that folder — no manual
registration needed.

**Contributions welcome** — open a pull request or ping the owners below.

---

## 🙋 Support

Questions, bugs, or feature requests — reach out to the owners directly:
[@Youradhey](https://t.me/Youradhey) · [@sunradhey](https://t.me/sunradhey)

### ⭐ If this project helped you, consider leaving a star!

**[👉 Click here to star this repo](https://github.com/YOUR_USERNAME/YOUR_REPO)**

---

#RADHEY
