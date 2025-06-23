from fastapi import FastAPI, Request
import os
import telegram

app = FastAPI()

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/")
async def handle_webhook(request: Request):
    payload = await request.json()
    print("Received webhook payload:", payload)

    if "message" in payload:
        chat_id = payload["message"]["chat"]["id"]
        text = payload["message"].get("text", "")

        if text == "/start":
            await bot.send_message(chat_id=chat_id, text="Просто пришли ссылку, и я скачаю!")

    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
