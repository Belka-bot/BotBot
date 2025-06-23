from fastapi import FastAPI, Request
import os
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

app = FastAPI()
bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/")
async def handle_webhook(request: Request):
    payload = await request.json()
    if "message" in payload and "text" in payload["message"]:
        chat_id = payload["message"]["chat"]["id"]
        text = payload["message"]["text"]
        if text.startswith("/start"):
            keyboard = [
                [InlineKeyboardButton("Скачать MP3", callback_data='mp3')],
                [InlineKeyboardButton("720p", callback_data='720p')],
                [InlineKeyboardButton("1080p", callback_data='1080p')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await bot.send_message(chat_id=chat_id, text="Просто пришли ссылку, и я скачаю!", reply_markup=reply_markup)
    return {"status": "received"}
