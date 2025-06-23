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
async def webhook(request: Request):
    data = await request.json()
# Получаем ID отправителя
if 'message' in payload:
    sender = payload['message']['from']['id']
    bot_id = bot.get_me().id

    # Если отправитель — сам бот, игнорируем
    if sender == bot_id:
        return {"status": "ignored"}
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            keyboard = [
                [InlineKeyboardButton("🎵 Скачать MP3", callback_data="audio")],
                [InlineKeyboardButton("144p", callback_data="144p"),
                 InlineKeyboardButton("240p", callback_data="240p")],
                [InlineKeyboardButton("360p", callback_data="360p"),
                 InlineKeyboardButton("480p", callback_data="480p")],
                [InlineKeyboardButton("720p", callback_data="720p"),
                 InlineKeyboardButton("1080p", callback_data="1080p")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await bot.send_message(chat_id=chat_id, text="Просто пришли ссылку, и я скачаю!", reply_markup=reply_markup)

    return {"ok": True}
