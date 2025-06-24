from fastapi import FastAPI, Request
import uvicorn
import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CallbackContext, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from yt_dlp import YoutubeDL
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
app = FastAPI()
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

last_links = set()

def build_keyboard(formats):
    buttons = []
    for fmt in formats:
        buttons.append([InlineKeyboardButton(fmt["text"], callback_data=fmt["url"])])
    return InlineKeyboardMarkup(buttons)

def get_formats(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                text = f"{f['format_note']} / {round(f['filesize'] / 1024 / 1024, 1) if f.get('filesize') else '?'} MB"
                formats.append({"text": text, "url": f['url']})
        if info.get('url'):
            formats.append({"text": "Скачать MP3", "url": info['url']})
        return formats

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Просто пришли ссылку, и я скачаю!")

def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    if url in last_links:
        return
    last_links.add(url)
    try:
        formats = get_formats(url)
        keyboard = build_keyboard(formats)
        update.message.reply_text("Выберите формат:", reply_markup=keyboard)
    except Exception as e:
        update.message.reply_text("Ошибка при обработке ссылки.")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text(f"🔗 {query.data}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
dispatcher.add_handler(CallbackQueryHandler(button))

@app.post("/")
async def process_update(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"ok": True}