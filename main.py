
from fastapi import FastAPI, Request
import os
import telegram

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

recent_links = set()

@app.post("/")
async def handle_webhook(request: Request):
    payload = await request.json()
    print("Received webhook payload:", payload)

    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if "http" in text:
        if text in recent_links:
            print("Duplicate link ignored:", text)
            return {"status": "duplicate"}

        recent_links.add(text)
        if len(recent_links) > 20:
            recent_links.pop()

        # Здесь должна быть логика отправки кнопок и обработки ссылки
        print("Processing new link:", text)

    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
