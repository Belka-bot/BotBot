from fastapi import FastAPI, Request
import os
import telegram
import json

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)
last_message_id = 0

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/")
async def handle_webhook(request: Request):
    global last_message_id
    payload = await request.json()
    print("Received webhook payload:", json.dumps(payload, indent=2))

    message = payload.get("message") or payload.get("channel_post")
    if not message:
        return {"status": "ignored"}

    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if message_id == last_message_id:
        print("Duplicate message detected. Skipping.")
        return {"status": "duplicate"}
    
    last_message_id = message_id

    if "youtube.com" in text or "youtu.be" in text:
        bot.send_message(chat_id=chat_id, text="Просто пришли ссылку, и я скачаю!",
                         reply_markup=telegram.InlineKeyboardMarkup([
                             [telegram.InlineKeyboardButton("Скачать MP3", callback_data="mp3")],
                             [telegram.InlineKeyboardButton("720p", callback_data="720p")],
                             [telegram.InlineKeyboardButton("1080p", callback_data="1080p")],
                         ]))
    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)