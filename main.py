import os
import re
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("RAILWAY_STATIC_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{DOMAIN}{WEBHOOK_PATH}"

app = FastAPI()
bot_app = Application.builder().token(BOT_TOKEN).build()

# Хранилище для защиты от повторных нажатий
processed_callbacks = set()

# Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто пришли ссылку, и я скачаю!")

# Кнопки выбора форматов
def build_keyboard(video_url: str):
    qualities = ["MP3", "144p", "240p", "360p", "480p", "720p", "1080p"]
    buttons = [[InlineKeyboardButton(text=q, callback_data=f"{q}|{video_url}")] for q in qualities]
    return InlineKeyboardMarkup(buttons)

# Автоответ на ссылку
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if re.search(r'(https?://)?(www\.)?(youtube|youtu\.be|vk\.com|tiktok\.com|rutube\.ru|twitter\.com)', text):
        keyboard = build_keyboard(text)
        await update.message.reply_text(
            f"🎬 Видео обнаружено!

Белка помогает вам скачать видео 🐿️",
            reply_markup=keyboard
        )

# Обработка нажатий
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data in processed_callbacks:
        await query.edit_message_text("⏳ Уже обрабатывается...")
        return
    processed_callbacks.add(query.data)
    quality, url = query.data.split("|", 1)
    await query.edit_message_text(
        f"🔗 Скачивание в формате {quality} запущено!

Белка помогает вам скачать видео 🐿️

URL: {url}"
    )

# Регистрация хендлеров
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
bot_app.add_handler(CallbackQueryHandler(handle_callback))

@app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook установлен:", WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    body = await req.json()
    update = Update.de_json(body, bot_app.bot)
    await bot_app.process_update(update)
    return "ok"
