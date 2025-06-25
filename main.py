from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "BelkaBot is working!"}# Здесь будет основной код бота
