
import os
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
import yt_dlp
from uuid import uuid4
import os

app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")
YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Хранилище ID сообщений для защиты от повторов
used_callback_ids = set()

@app.post("/webhook")
async def telegram_webhook(update: dict, background_tasks: BackgroundTasks):
    if "message" in update and "text" in update["message"]:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message["text"]

        if any(domain in text for domain in ["youtube.com", "youtu.be", "vk.com", "tiktok.com", "rutube.ru", "twitter.com"]):
            buttons = [
                [{"text": "MP3", "callback_data": f"mp3|{text}"}],
                [{"text": "144p", "callback_data": f"144|{text}"},
                 {"text": "240p", "callback_data": f"240|{text}"},
                 {"text": "360p", "callback_data": f"360|{text}"}],
                [{"text": "480p", "callback_data": f"480|{text}"},
                 {"text": "720p", "callback_data": f"720|{text}"},
                 {"text": "1080p", "callback_data": f"1080|{text}"}]
            ]
            await send_message(chat_id, "Белка помогает вам скачать видео", buttons)
    elif "callback_query" in update:
        callback = update["callback_query"]
        callback_id = callback["id"]
        if callback_id in used_callback_ids:
            return JSONResponse(content={"status": "duplicate"}, status_code=200)
        used_callback_ids.add(callback_id)
        data = callback["data"]
        chat_id = callback["message"]["chat"]["id"]
        format_code, url = data.split("|")
        background_tasks.add_task(handle_download, chat_id, url, format_code)
    return {"ok": True}

async def send_message(chat_id, text, buttons=None):
    payload = {"chat_id": chat_id, "text": text}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendMessage", json=payload)

async def handle_download(chat_id, url, format_code):
    temp_dir = "/tmp"
    file_id = str(uuid4())
    filepath = f"{temp_dir}/{file_id}.mp4" if format_code != "mp3" else f"{temp_dir}/{file_id}.mp3"

    ydl_opts = {
        "outtmpl": filepath,
        "format": "bestaudio/best" if format_code == "mp3" else f"bestvideo[height<={format_code}]+bestaudio/best",
        "merge_output_format": "mp4" if format_code != "mp3" else "mp3",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        size = os.path.getsize(filepath)
        if size < 49 * 1024 * 1024:
            async with httpx.AsyncClient() as client:
                with open(filepath, "rb") as f:
                    await client.post(
                        f"{API_URL}/sendDocument",
                        data={"chat_id": chat_id},
                        files={"document": f},
                    )
        else:
            link = await upload_to_yandex(filepath)
            await send_message(chat_id, f"Файл слишком большой. Скачай здесь: {link}")
    except Exception as e:
        await send_message(chat_id, f"Ошибка при скачивании: {str(e)}")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

async def upload_to_yandex(filepath):
    filename = os.path.basename(filepath)
    upload_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={filename}&overwrite=true"
    headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(upload_url, headers=headers)
        href = r.json()["href"]
        with open(filepath, "rb") as f:
            await client.put(href, content=f.read(), headers=headers)
    return f"https://disk.yandex.ru/d/{filename}"

@app.on_event("startup")
async def set_webhook():
    webhook_url = f"https://{WEBHOOK_DOMAIN}/webhook"
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/setWebhook", data={"url": webhook_url})
