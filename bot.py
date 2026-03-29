import telebot
from telebot import types
import yt_dlp
import requests
import os
import time

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

user_url = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Send video link")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text
    user_url[m.chat.id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("HD", callback_data="hd"),
        types.InlineKeyboardButton("SD", callback_data="sd")
    )

    bot.reply_to(m, "Select quality:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    url = user_url.get(call.message.chat.id)

    bot.send_message(call.message.chat.id, "Downloading...")

    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": "video.%(ext)s"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        with open(file, "rb") as f:
            bot.send_video(call.message.chat.id, f)

        os.remove(file)

    except:
        bot.send_message(call.message.chat.id, "Error!")

bot.infinity_polling()
