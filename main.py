
from fastapi import FastAPI, Request
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import yt_dlp
from yandex_disk import upload_to_yadisk

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"https://{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

formats = ["mp3", "144", "240", "360", "480", "720", "1080"]

@dp.message()
async def handle_message(message: types.Message):
    url = message.text.strip()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скачать видео", callback_data=f"download|{url}")],
        [InlineKeyboardButton(text="MP3", callback_data=f"mp3|{url}")]
    ])
    await message.reply_text(f"Белка помогает вам скачать видео: {url}", reply_markup=markup)

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    try:
        action, url = callback.data.split("|")
        await callback.answer("Скачиваю...", show_alert=False)
        filename = f"{action}_{abs(hash(url))}.mp4" if action != "mp3" else f"{action}_{abs(hash(url))}.mp3"

        ydl_opts = {
            "outtmpl": f"/tmp/{filename}",
            "format": f"bestvideo[height<={action}]+bestaudio/best" if action.isdigit() else "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3"
            }] if action == "mp3" else []
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_path = f"/tmp/{filename}"
        file_size = os.path.getsize(file_path)

        if file_size > 49_000_000:
            link = upload_to_yadisk(file_path)
            await bot.send_message(callback.message.chat.id, f"Файл больше 50MB, вот ссылка:
{link}")
        else:
            with open(file_path, "rb") as f:
                await bot.send_document(callback.message.chat.id, f)
    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
