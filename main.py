import os
from fastapi import FastAPI, Request
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RAILWAY_STATIC_URL')}{WEBHOOK_PATH}"

app = FastAPI()
bot_app = Application.builder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто пришли ссылку, и я скачаю!")

bot_app.add_handler(CommandHandler("start", start))

@app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook установлен:", WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    body = await req.json()
    update = telegram.Update.de_json(body, bot_app.bot)
    await bot_app.process_update(update)
    return "ok"
