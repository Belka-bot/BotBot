
from fastapi import FastAPI, Request
import uvicorn
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from yt_dlp import YoutubeDL
import os
import aiohttp
import aiofiles
import uuid
from yandex_disk import upload_to_yandex_disk

TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("WEBHOOK_DOMAIN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{DOMAIN}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = FastAPI()

def build_keyboard(video_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скачать MP3", callback_data=f"mp3|{video_id}")],
        [InlineKeyboardButton(text="720p", callback_data=f"720|{video_id}")],
        [InlineKeyboardButton(text="1080p", callback_data=f"1080|{video_id}")]
    ])

@dp.message()
async def handle_message(message: types.Message):
    if "http" in message.text:
        await message.answer("🔍 Обрабатываю ссылку...")
        video_id = str(uuid.uuid4())
        await message.answer(f"Белка помогает вам скачать видео:", reply_markup=build_keyboard(video_id))

@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    format_code, video_id = call.data.split("|")
    url = call.message.reply_to_message.text.strip()
    ydl_opts = {
        "format": "bestaudio/best" if format_code == "mp3" else "bestvideo+bestaudio[ext=mp4]",
        "outtmpl": f"/tmp/{video_id}.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }] if format_code == "mp3" else [],
    }
    await call.answer("⏬ Скачиваю...")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        if format_code == "mp3":
            file_path = file_path.replace(".webm", ".mp3").replace(".m4a", ".mp3")
    size_mb = os.path.getsize(file_path) / 1024 / 1024
    if size_mb > 47:
        link = await upload_to_yandex_disk(file_path)
        await call.message.answer(f"⚠️ Файл больше 50MB
💾 Скачайте по ссылке:
{link}")
    else:
        async with aiofiles.open(file_path, "rb") as f:
            await call.message.answer_document(types.FSInputFile(file_path, filename=os.path.basename(file_path)))
    os.remove(file_path)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    body = await req.body()
    await dp.feed_update(bot, req.headers, body)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
