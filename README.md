# 🤖 Radhey — Instagram Downloader & Group Guardian Bot

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)
[![Framework](https://img.shields.io/badge/Framework-Pyrogram-2AA9EE)](https://docs.pyrogram.org/)
[![Platform](https://img.shields.io/badge/Platform-Render%20%7C%20VPS%20%7C%20Termux-orange)]()
[![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen)]()

An all-in-one Telegram bot that downloads Instagram reels/posts/videos with a **live progress bar**, plus full **group moderation** — built with **Pyrogram**, **yt-dlp**, **instaloader**, and **Flask**.

**Owner:** [@Youradhey](https://t.me/Youradhey) · [@sunradhey](https://t.me/sunradhey)

---

## 📚 Table of Contents

- [Features](#-features)
- [Use Cases](#-use-cases)
- [Installation](#-installation)
  - [Termux Setup](#termux-android)
  - [Linux / Windows Setup](#linux--windows)
  - [Render Setup](#render-deployment)
- [Configuration](#️-configuration)
- [Command Reference](#️-command-reference)
- [Developer](#-developer)

---

## ✨ Features

- 📥 **Instant downloads** — send any Instagram reel/post/video link in DM or group
- 📊 **Live progress bar** — real-time download and upload progress
- 📝 **Show Caption button** — one tap to see the original post caption
- 🌐 **Web Downloader** — users can also download reels directly from the website
- 🔒 **Force-subscribe gate** — users must join `@xivasudev` before using in DM
- 👮 **Full group moderation** — mute, unmute, ban, unban, kick, promote, demote, pin, unpin, purge, warn
- 📢 **Owner broadcast** — message every user or every group instantly
- 🙋 **Rich /start** — shows user info + profile picture
- ⚡ **Self-installing** — missing packages auto-install on first run

---

## 💡 Use Cases

- **Content Saving** — save reels you want to keep or repost
- **Community Moderation** — manage your group without doing it manually
- **Channel Growth** — force-subscribe gate grows your channel alongside the bot
- **Announcements** — broadcast to all users or groups in one command

---

## 📦 Installation

### Termux (Android)

Copy and paste this entire block into Termux:

```bash
pkg install python git -y && git clone https://github.com/diractory/insta-downloader.git && cd insta-downloader && python bot.py
```

That's it — dependencies install automatically on first run.

### Linux / Windows

```bash
git clone https://github.com/diractory/insta-downloader.git
cd insta-downloader
cp .env.example .env
# Edit .env and fill in your values
python bot.py
```

### Render Deployment

```
Build Command  : pip install -r requirements.txt
Start Command  : python bot.py
```

Go to your service → **Environment** tab → add these variables one by one:

| Key | Value |
|---|---|
| `API_ID` | From `my.telegram.org` |
| `API_HASH` | From `my.telegram.org` |
| `BOT_TOKEN` | From `@BotFather` |
| `OWNER_IDS` | Your numeric Telegram ID |
| `FORCE_SUB_CHANNEL` | `xivasudev` |
| `BOT_NAME` | `Radhey Downloader` |

---

## ⚙️ Configuration

All settings go in environment variables — **never hardcode secrets in a public repo.**

Get your `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org) → API Development Tools.

Get your bot token from [@BotFather](https://t.me/BotFather).

Get your numeric Telegram ID from [@userinfobot](https://t.me/userinfobot).

---

## 🗒️ Command Reference

| Command | Where | Who | Description |
|---|---|---|---|
| `/start` | DM / Group | Everyone | Start the bot, shows your info + PFP |
| `(paste IG link)` | DM / Group | Everyone | Downloads with live progress bar |
| `/dl <link>` | DM / Group | Everyone | Force-download a specific link |
| `/mute` `/unmute` | Group | Admin | Restrict or restore messaging rights |
| `/ban` `/unban` `/kick` | Group | Admin | Remove members |
| `/promote` `/demote` | Group | Admin | Manage admin rights |
| `/warn` `/resetwarn` | Group | Admin | 3 warnings = auto ban |
| `/purge` `/pin` `/unpin` | Group | Admin | Bulk delete and pin control |
| `/id` `/info` `/ping` | Anywhere | Everyone | Utility commands |
| `/broadcast` `/gbroadcast` | DM | Owner | Message all users / all groups |
| `/stats` | DM | Owner | View bot stats |

---

## 👨‍💻 Developer

Made with ❤️ by [@Youradhey](https://t.me/Youradhey) and [@sunradhey](https://t.me/sunradhey)

For support or questions, DM the owners directly on Telegram.

---

## ⭐ Support the Project

If this bot helped you, please consider leaving a star on the repo — it helps a lot!

**[👉 Click here to leave a ⭐ star on this repo](https://github.com/diractory/insta-downloader)**

---

#RADHEY
<!-- hacktoberfest update 20260712154352297736 -->
<!-- run 1 @ 20260712154411515968 -->
<!-- run 2 @ 20260712154424824505 -->
<!-- run 3 @ 20260712154437744477 -->
<!-- run 4 @ 20260712154450219302 -->
<!-- run 5 @ 20260712154503581805 -->
<!-- run 6 @ 20260712154516844085 -->
<!-- run 7 @ 20260712154530006074 -->
<!-- run 8 @ 20260712154543159451 -->
<!-- run 9 @ 20260712154555590649 -->
<!-- run 10 @ 20260712154607989171 -->
<!-- run 11 @ 20260712154621525954 -->
<!-- run 12 @ 20260712154634450519 -->
<!-- run 13 @ 20260712154648193190 -->
<!-- run 14 @ 20260712154701627633 -->
<!-- run 15 @ 20260712154715101012 -->
<!-- run 16 @ 20260712154728229465 -->
<!-- run 17 @ 20260712154739701355 -->
<!-- run 18 @ 20260712154752068802 -->
<!-- run 19 @ 20260712154805111991 -->
<!-- run 20 @ 20260712154816426051 -->
<!-- run 21 @ 20260712154828425603 -->
<!-- run 22 @ 20260712154842271917 -->
<!-- run 23 @ 20260712154854075983 -->
<!-- run 24 @ 20260712154906446599 -->
<!-- run 25 @ 20260712154918063399 -->
<!-- run 26 @ 20260712154935062589 -->
<!-- run 27 @ 20260712154948615493 -->
<!-- run 28 @ 20260712155001982040 -->
<!-- run 29 @ 20260712155019121076 -->
<!-- run 30 @ 20260712155031148418 -->
<!-- run 31 @ 20260712155043066600 -->
<!-- run 32 @ 20260712155055652202 -->
<!-- run 33 @ 20260712155107836264 -->
<!-- run 34 @ 20260712155121239732 -->
<!-- run 35 @ 20260712155135619772 -->
<!-- run 36 @ 20260712155148222812 -->
<!-- run 37 @ 20260712155200964259 -->
