import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import os
import threading
from flask import Flask
from pymongo import MongoClient
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN = int(os.environ.get("ADMIN", "0"))
PORT = int(os.environ.get("PORT", "8080"))
MONGO_URL = os.environ.get(
    "MONGO_URL",
    "mongodb+srv://wasdimu:xivasudev@cluster0.zjkb7od.mongodb.net/?appName=Cluster0",
)

FORCE_SUB_CHANNELS = ["xivasudev", "sunradhey"]
FEEDBACK_CHANNEL = -1003513807071
CREDIT_TEXT = "**Credits: @Youradhey | @sunradhey**\n**Channel: @xivasudev**"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

mongo = MongoClient(MONGO_URL)
db = mongo["rename_bot"]
users_col = db["users"]
banned_col = db["banned"]
clones_col = db["clones"]

user_state = {}

def add_user(user_id):
    users_col.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

def get_all_users():
    return [u["_id"] for u in users_col.find({}, {"_id": 1})]

def ban_user(user_id):
    banned_col.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

def unban_user(user_id):
    banned_col.delete_one({"_id": user_id})

def is_banned(user_id):
    return banned_col.find_one({"_id": user_id}) is not None

def save_clone(owner_id, token):
    clones_col.update_one(
        {"_id": token}, {"$set": {"owner": owner_id, "token": token}}, upsert=True
    )

def get_all_clones():
    return list(clones_col.find({}))

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

def get_state(user_id):
    if user_id not in user_state:
        user_state[user_id] = {
            "file": None,
            "thumb": None,
            "caption": None,
            "rename": None,
            "waiting": None,
        }
    return user_state[user_id]

def join_markup():
    buttons = [
        [InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch}")]
        for ch in FORCE_SUB_CHANNELS
    ]
    buttons.append([InlineKeyboardButton("🔄 Try Again", callback_data="check_join")])
    return InlineKeyboardMarkup(buttons)

async def is_joined(client: Client, user_id: int):
    for ch in FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in ("left", "banned"):
                return False
        except UserNotParticipant:
            return False
        except Exception:
            return False
    return True

def file_menu_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Rename", callback_data="menu_rename")],
        [InlineKeyboardButton("🖼️ Add Thumbnail", callback_data="menu_thumb")],
        [InlineKeyboardButton("📝 Add Caption", callback_data="menu_caption")],
        [InlineKeyboardButton("✅ Done / Download", callback_data="menu_done")],
        [InlineKeyboardButton("♻️ Reset", callback_data="menu_reset")],
    ])

def start_menu_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧬 Clone This Bot", callback_data="clone_bot")],
    ])

async def send_start_menu(message: Message):
    await message.reply_text(
        "**👋 Welcome!**\n\n"
        "**📤 Send me any file (document/video) to get started.**\n\n"
        "**You can then:**\n"
        "**✏️ Rename it**\n"
        "**🖼️ Add a thumbnail**\n"
        "**📝 Add a caption**\n"
        "**✅ Download the final file**\n\n"
        f"{CREDIT_TEXT}",
        reply_markup=start_menu_markup(),
    )

async def start_handler(client: Client, message: Message):
    add_user(message.from_user.id)
    if is_banned(message.from_user.id):
        await message.reply_text("**🚫 You are banned from using this bot.**")
        return
    if getattr(client, "is_main", False):
        if not await is_joined(client, message.from_user.id):
            await message.reply_text(
                "**🔒 You must join our channels to use this bot.**",
                reply_markup=join_markup(),
            )
            return
    await send_start_menu(message)

async def check_join_handler(client: Client, cb: CallbackQuery):
    if await is_joined(client, cb.from_user.id):
        await cb.message.edit_text("**✅ Access granted! Send me a file to begin.**")
    else:
        await cb.answer("❗ You haven't joined all channels yet.", show_alert=True)

async def feedback_command(client: Client, message: Message):
    get_state(message.from_user.id)["waiting"] = "feedback"
    await message.reply_text("**💬 Send your feedback message now.**")

async def broadcast_handler(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("**❗ Reply to a message with /broad to broadcast it.**")
        return

    users = get_all_users()
    status = await message.reply_text(f"**📢 Broadcasting to {len(users)} users...**")

    sent, failed = 0, 0
    for uid in users:
        try:
            await message.reply_to_message.forward(uid)
            sent += 1
        except Exception:
            failed += 1

    await status.edit_text(
        f"**✅ Broadcast complete!**\n\n"
        f"**Sent:** {sent}\n"
        f"**Failed:** {failed}"
    )

async def ban_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("**❗ Usage: /ban user_id**")
        return
    try:
        uid = int(message.command[1])
    except ValueError:
        await message.reply_text("**❗ Invalid user id.**")
        return
    ban_user(uid)
    await message.reply_text(f"**🚫 User `{uid}` has been banned.**")

async def unban_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("**❗ Usage: /unban user_id**")
        return
    try:
        uid = int(message.command[1])
    except ValueError:
        await message.reply_text("**❗ Invalid user id.**")
        return
    unban_user(uid)
    await message.reply_text(f"**✅ User `{uid}` has been unbanned.**")

async def clone_command(client: Client, message: Message):
    get_state(message.from_user.id)["waiting"] = "clone_token"
    await message.reply_text(
        "**🧬 Send me your bot token from @BotFather to clone this bot.**"
    )

async def clone_callback(client: Client, cb: CallbackQuery):
    get_state(cb.from_user.id)["waiting"] = "clone_token"
    await cb.message.reply_text(
        "**🧬 Send me your bot token from @BotFather to clone this bot.**"
    )
    await cb.answer()

async def file_handler(client: Client, message: Message):
    add_user(message.from_user.id)
    if is_banned(message.from_user.id):
        await message.reply_text("**🚫 You are banned from using this bot.**")
        return
    if getattr(client, "is_main", False):
        if not await is_joined(client, message.from_user.id):
            await message.reply_text(
                "**🔒 You must join our channels to use this bot.**",
                reply_markup=join_markup(),
            )
            return

    state = get_state(message.from_user.id)
    state["file"] = message
    state["thumb"] = None
    state["caption"] = None
    state["rename"] = None
    state["waiting"] = None

    await message.reply_text(
        "**📁 File received! Choose an option below:**",
        reply_markup=file_menu_markup(),
    )

async def menu_rename(client: Client, cb: CallbackQuery):
    state = get_state(cb.from_user.id)
    if not state["file"]:
        await cb.answer("❗ Send a file first.", show_alert=True)
        return
    state["waiting"] = "rename"
    await cb.message.reply_text("**✏️ Send the new filename (with extension).**")
    await cb.answer()

async def menu_thumb(client: Client, cb: CallbackQuery):
    state = get_state(cb.from_user.id)
    if not state["file"]:
        await cb.answer("❗ Send a file first.", show_alert=True)
        return
    state["waiting"] = "thumb"
    await cb.message.reply_text("**🖼️ Now send a photo to set as thumbnail.**")
    await cb.answer()

async def menu_caption(client: Client, cb: CallbackQuery):
    state = get_state(cb.from_user.id)
    if not state["file"]:
        await cb.answer("❗ Send a file first.", show_alert=True)
        return
    state["waiting"] = "caption"
    await cb.message.reply_text("**📝 Send the caption text.**")
    await cb.answer()

async def menu_reset(client: Client, cb: CallbackQuery):
    user_state[cb.from_user.id] = {
        "file": None, "thumb": None, "caption": None, "rename": None, "waiting": None
    }
    await cb.message.reply_text("**♻️ Reset done. Send a new file to start again.**")
    await cb.answer()

async def menu_done(client: Client, cb: CallbackQuery):
    state = get_state(cb.from_user.id)
    if not state["file"]:
        await cb.answer("❗ Send a file first.", show_alert=True)
        return

    status = await cb.message.reply_text("**⏳ Processing your file...**")
    user_dir = os.path.join(DOWNLOAD_DIR, str(cb.from_user.id))
    os.makedirs(user_dir, exist_ok=True)

    original = state["file"]
    file_path = await original.download(file_name=os.path.join(user_dir, ""))

    if state["rename"]:
        new_path = os.path.join(user_dir, state["rename"])
        os.rename(file_path, new_path)
        file_path = new_path

    caption_text = state["caption"] or CREDIT_TEXT

    await status.edit_text("**⏳ Uploading final file...**")

    await client.send_document(
        chat_id=cb.from_user.id,
        document=file_path,
        thumb=state["thumb"],
        caption=caption_text,
    )

    if os.path.exists(file_path):
        os.remove(file_path)
    if state["thumb"] and os.path.exists(state["thumb"]):
        os.remove(state["thumb"])

    user_state[cb.from_user.id] = {
        "file": None, "thumb": None, "caption": None, "rename": None, "waiting": None
    }
    await status.delete()
    await cb.answer()

async def photo_handler(client: Client, message: Message):
    state = get_state(message.from_user.id)
    if state["waiting"] == "thumb":
        user_dir = os.path.join(DOWNLOAD_DIR, str(message.from_user.id))
        os.makedirs(user_dir, exist_ok=True)
        thumb_path = os.path.join(user_dir, "thumb.jpg")
        await message.download(file_name=thumb_path)
        state["thumb"] = thumb_path
        state["waiting"] = None
        await message.reply_text(
            "**✅ Thumbnail set!**",
            reply_markup=file_menu_markup(),
        )

async def text_handler(client: Client, message: Message):
    if message.text.startswith("/"):
        return

    state = get_state(message.from_user.id)

    if state["waiting"] == "rename":
        state["rename"] = message.text.strip()
        state["waiting"] = None
        await message.reply_text(
            f"**✅ Rename set to:** `{state['rename']}`",
            reply_markup=file_menu_markup(),
        )

    elif state["waiting"] == "caption":
        state["caption"] = message.text
        state["waiting"] = None
        await message.reply_text(
            "**✅ Caption set!**",
            reply_markup=file_menu_markup(),
        )

    elif state["waiting"] == "feedback":
        state["waiting"] = None
        user = message.from_user
        await client.send_message(
            FEEDBACK_CHANNEL,
            f"**📩 New Feedback**\n\n"
            f"**From:** {user.mention} (`{user.id}`)\n\n"
            f"**Message:**\n{message.text}"
        )
        await message.reply_text("**✅ Thanks! Your feedback has been sent.**")

    elif state["waiting"] == "clone_token":
        state["waiting"] = None
        if not users_col.find_one({"_id": message.from_user.id}):
            await message.reply_text(
                "**❗ Please start the main bot first with /start, then try cloning again.**"
            )
            return
        token = message.text.strip()
        status = await message.reply_text("**⏳ Starting your cloned bot...**")
        try:
            clone_app = Client(
                name=f"clone_{token.split(':')[0]}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                in_memory=True,
            )
            clone_app.is_main = False
            register_handlers(clone_app)
            await clone_app.start()
            save_clone(message.from_user.id, token)
            me = await clone_app.get_me()
            await status.edit_text(
                f"**✅ Your bot @{me.username} is now live and working just like this one!**"
            )
        except Exception as e:
            await status.edit_text(f"**❌ Failed to start your bot.**\n`{e}`")

def register_handlers(client: Client):
    client.add_handler(MessageHandler(start_handler, filters.command("start")))
    client.add_handler(CallbackQueryHandler(check_join_handler, filters.regex("^check_join$")))
    client.add_handler(MessageHandler(feedback_command, filters.command("feedback")))
    client.add_handler(MessageHandler(broadcast_handler, filters.command("broad") & filters.user(ADMIN)))
    client.add_handler(MessageHandler(ban_command, filters.command("ban") & filters.user(ADMIN)))
    client.add_handler(MessageHandler(unban_command, filters.command("unban") & filters.user(ADMIN)))
    client.add_handler(MessageHandler(clone_command, filters.command("clone")))
    client.add_handler(CallbackQueryHandler(clone_callback, filters.regex("^clone_bot$")))
    client.add_handler(MessageHandler(file_handler, filters.document | filters.video))
    client.add_handler(CallbackQueryHandler(menu_rename, filters.regex("^menu_rename$")))
    client.add_handler(CallbackQueryHandler(menu_thumb, filters.regex("^menu_thumb$")))
    client.add_handler(CallbackQueryHandler(menu_caption, filters.regex("^menu_caption$")))
    client.add_handler(CallbackQueryHandler(menu_reset, filters.regex("^menu_reset$")))
    client.add_handler(CallbackQueryHandler(menu_done, filters.regex("^menu_done$")))
    client.add_handler(MessageHandler(photo_handler, filters.photo))
    client.add_handler(MessageHandler(text_handler, filters.text & ~filters.via_bot))

async def main():
    bot = Client("RenameBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=100)
    bot.is_main = True
    register_handlers(bot)
    await bot.start()
    for clone in get_all_clones():
        try:
            token = clone["token"]
            clone_app = Client(
                name=f"clone_{token.split(':')[0]}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                in_memory=True,
            )
            clone_app.is_main = False
            register_handlers(clone_app)
            await clone_app.start()
        except Exception as e:
            print(f"Failed to restart clone: {e}")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
