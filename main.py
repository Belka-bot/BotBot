
from fastapi import FastAPI, Request
import uvicorn
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
import logging

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = FastAPI()
bot_app = Application.builder().token(TOKEN).build()

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто пришли ссылку, и я скачаю!")

# Обработка сообщений с ссылками
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton("MP3", callback_data=f"mp3|{url}"),
         InlineKeyboardButton("480", callback_data=f"480|{url}"),
         InlineKeyboardButton("720p", callback_data=f"720p|{url}"),
         InlineKeyboardButton("1080p", callback_data=f"1080p|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Белка помогает вам скачать видео:\n{url}", reply_markup=reply_markup)

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quality, url = query.data.split("|")
    filename = f"downloaded.{'mp3' if quality == 'mp3' else 'mp4'}"
    ydl_opts = {
        'format': 'bestaudio/best' if quality == 'mp3' else f'bestvideo[height<={quality.replace("p", "")}]+bestaudio/best',
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if quality == 'mp3' else []
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    await query.edit_message_text(f"Скачано ({quality}): {url}")

# Основной запуск
async def main():
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.add_handler(CallbackQueryHandler(button_handler))

    await bot_app.initialize()
    await bot_app.start()
    await bot_app.bot.set_webhook(WEBHOOK_URL)

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
