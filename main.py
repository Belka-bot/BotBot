
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
    if not url.startswith("http"):
        await message.answer("Отправь корректную ссылку на видео.")
        return

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{fmt}p" if fmt.isdigit() else fmt.upper(), callback_data=f"{fmt}|{url}")]
        for fmt in formats
    ])
    await message.answer(f"Белка помогает вам скачать видео: {url}", reply_markup=markup)

@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    fmt, url = data.split("|")
    await callback_query.answer("Готовим файл...")

    ydl_opts = {
        'format': f'bestaudio/best' if fmt == 'mp3' else f'bestvideo[height<={fmt}]+bestaudio/best',
        'outtmpl': f'{fmt}_video.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4' if fmt != 'mp3' else 'mp3'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        await callback_query.message.answer(f"Ошибка загрузки: {str(e)}")
        return

    if os.path.getsize(filename) > 45 * 1024 * 1024:
        yadisk_url = upload_to_yadisk(filename)
        await callback_query.message.answer(
            f"Файл слишком большой. Скачай через Яндекс.Диск:
{yadisk_url}"
        )
    else:
        await callback_query.message.answer_document(types.FSInputFile(filename))

    os.remove(filename)

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}
