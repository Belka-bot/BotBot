from fastapi import FastAPI, Request
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import yt_dlp
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"https://{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

@dp.message()
async def handle_message(message: types.Message):
    url = message.text.strip()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скачать видео", callback_data=f"download|{url}")],
        [InlineKeyboardButton(text="MP3", callback_data=f"mp3|{url}")]
    ])
    await message.reply(f"Белка помогает вам скачать видео: {url}", reply_markup=markup)

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    action, url = callback.data.split("|")
    await callback.answer("Скачиваю...")
    filename = "video.mp4" if action == "download" else "audio.mp3"
    ydl_opts = {
        "outtmpl": f"/tmp/{filename}",
        "format": "bestaudio" if action == "mp3" else "best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }] if action == "mp3" else []
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    with open(f"/tmp/{filename}", "rb") as f:
        await bot.send_document(callback.message.chat.id, f)

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
