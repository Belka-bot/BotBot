import uvicorn
import os
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    # обработка webhook
    return {"status": "received"}

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/")
async def handle_webhook(request: Request):
    payload = await request.json()
    print("Received webhook payload:", payload)
    return {"status": "received"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)