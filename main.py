from fastapi import FastAPI, Request
import os
import telegram

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/")
async def handle_webhook(request: Request):
    payload = await request.json()

    # Предотвращение самоповторов
    if 'message' in payload:
        sender = payload['message']['from']['id']
        bot_id = bot.get_me().id
        if sender == bot_id:
            return {"status": "ignored"}

    print("Received webhook payload:", payload)
    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
