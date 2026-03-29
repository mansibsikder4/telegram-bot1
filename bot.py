import telebot
from telebot import types
import yt_dlp
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

user_url = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Send TikTok / YouTube / Facebook link")

# HANDLE MESSAGE
@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text

    if any(x in url for x in ["tiktok.com", "youtube.com", "youtu.be", "facebook.com"]):
        user_url[m.chat.id] = url

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🎬 HD", callback_data="hd"),
            types.InlineKeyboardButton("📉 SD", callback_data="sd")
        )

        bot.reply_to(m, "🎛 Select Quality:", reply_markup=markup)
    else:
        bot.reply_to(m, "❌ Invalid link")

# DOWNLOAD FUNCTION (FIXED)
def download(url, quality):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": "video.%(ext)s",
        "noplaylist": True,
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    url = user_url.get(call.message.chat.id)
    quality = call.data

    bot.send_message(call.message.chat.id, "⬇️ Downloading...")

    try:
        file = download(url, quality)

        with open(file, "rb") as f:
            bot.send_video(call.message.chat.id, f)

        os.remove(file)

        bot.send_message(call.message.chat.id, "✅ Done!")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Failed!\n{e}")

# RUN BOT
bot.infinity_polling(skip_pending=True)
