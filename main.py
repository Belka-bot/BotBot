import os
import re
import asyncio
import uuid
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from yt_dlp import YoutubeDL
import yadisk

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("RAILWAY_STATIC_URL")
YA_TOKEN = os.getenv("YANDEX_TOKEN")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{DOMAIN}{WEBHOOK_PATH}"

app = FastAPI()
bot_app = Application.builder().token(BOT_TOKEN).build()
processed_callbacks = set()
y = yadisk.YaDisk(token=YA_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто пришли ссылку, и я скачаю!")

def build_keyboard(video_url: str):
    qualities = ["MP3", "144p", "240p", "360p", "480p", "720p", "1080p"]
    buttons = [[InlineKeyboardButton(text=q, callback_data=f"{q}|{video_url}")] for q in qualities]
    return InlineKeyboardMarkup(buttons)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if re.search(r'(https?://)?(www\.)?(youtube|youtu\.be|vk\.com|tiktok\.com|rutube\.ru|twitter\.com)', text):
        keyboard = build_keyboard(text)
        await update.message.reply_text("🎬 Видео обнаружено!

Белка помогает вам скачать видео 🐿️", reply_markup=keyboard)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data in processed_callbacks:
        await query.edit_message_text("⏳ Уже обрабатывается...")
        return
    processed_callbacks.add(query.data)

    quality, url = query.data.split("|", 1)
    await query.edit_message_text(f"🔗 Скачивание {quality} началось...
Белка помогает вам скачать видео 🐿️")

    ext = "mp3" if quality == "MP3" else "mp4"
    output_name = f"/tmp/{uuid.uuid4()}.{ext}"

    ydl_opts = {
        'outtmpl': output_name,
        'format': 'bestaudio/best' if quality == "MP3" else f'bestvideo[height<={quality.replace("p","")}]+bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }] if quality == "MP3" else [],
        'merge_output_format': 'mp4'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        file_size = os.path.getsize(output_name)

        if file_size < 49 * 1024 * 1024:
            await context.bot.send_document(chat_id=query.message.chat_id, document=open(output_name, "rb"))
        else:
            remote_path = f"/BelkaBot/{os.path.basename(output_name)}"
            y.upload(output_name, remote_path)
            link = y.get_download_link(remote_path)
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"📁 Файл больше 50 МБ
🔗 Скачать с Яндекс.Диска: {link}")
    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❌ Ошибка: {str(e)}")

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
