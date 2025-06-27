
from fastapi import FastAPI
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import yt_dlp
import logging
import os
import uvicorn

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_DOMAIN")

app = FastAPI()
application = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто пришли ссылку, и я скачаю!")

# Обработка ссылок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton("MP3", callback_data=f"mp3|{url}")],
        [InlineKeyboardButton("480p", callback_data=f"480|{url}")],
        [InlineKeyboardButton("720p", callback_data=f"720|{url}")],
        [InlineKeyboardButton("1080p", callback_data=f"1080|{url}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Белка помогает вам скачать видео:
{url}", reply_markup=reply_markup)

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quality, url = query.data.split("|")
    await query.edit_message_text(f"Скачиваю {quality} версию видео...
{url}")
    # здесь может быть логика скачивания

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(WEBHOOK_URL)
