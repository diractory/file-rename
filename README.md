<p align="center">
  <img src="https://envs.sh/eer.jpg" width="150" alt="banner"/>
</p>

<h1 align="center">✨ ReNameX Bot ✨</h1>

<p align="center">
  A powerful Telegram bot to <b>rename</b>, <b>add thumbnails</b>, and <b>set captions</b> for your files — with clone support, broadcast, and force-subscribe.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Pyrogram-2.0-orange?style=for-the-badge&logo=telegram" />
  <img src="https://img.shields.io/badge/MongoDB-Database-green?style=for-the-badge&logo=mongodb" />
  <img src="https://img.shields.io/badge/Deploy-Render-purple?style=for-the-badge&logo=render" />
</p>

---

## 🚀 Features

- ✏️ **Rename** any document/video with a custom filename
- 🖼️ **Add Thumbnail** to your files
- 📝 **Add Caption** before sending
- 🧬 **Clone This Bot** — anyone can host their own copy using their bot token
- 🔒 **Force Subscribe** — users must join required channels (main bot only)
- 📢 **Broadcast** — admin can forward a message to all users
- 🚫 **Ban / Unban** — admin can restrict users
- 💬 **Feedback System** — user feedback forwarded to a private channel
- 🗄️ **MongoDB** — persistent storage for users, bans, and clones

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `ADMIN` | Your Telegram user ID |
| `PORT` | Port for the health-check web server (e.g. `8080`) |
| `MONGO_URL` | MongoDB connection string |
| `PYTHON_VERSION` | `3.11.9` (recommended on Render) |

---

## 📦 Deployment (Render)

```bash
Build Command: pip install -r requirements.txt
Start Command: python bot.py
```

1. Fork/clone this repository
2. Create a new **Web Service** on [Render](https://render.com)
3. Add the environment variables listed above
4. Deploy 🎉

---

## 🤖 Commands

```
/start        - Start the bot
/clone        - Clone this bot with your own token
/feedback     - Send feedback to the developer
/broad        - (Admin) Broadcast a replied message to all users
/ban <id>     - (Admin) Ban a user
/unban <id>   - (Admin) Unban a user
```

---

## 🧠 Tech Stack

- [Pyrogram](https://docs.pyrogram.org/) — Telegram MTProto framework
- [Flask](https://flask.palletsprojects.com/) — Health-check web server
- [MongoDB](https://www.mongodb.com/) — Database

---

## 👤 Credits

```
Developer   : t.me/Youradhey
Channel     : t.me/xivasudev
```

---

## ⭐ Support

If you found this project useful, consider giving it a star!

```
https://github.com/diractory/file-rename.git
```

<p align="center">
  Made with ❤️ by <b>@Youradhey</b>
</p>
