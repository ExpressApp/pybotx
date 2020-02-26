from fastapi import FastAPI

from bot.bot import bot

app = FastAPI()


@app.get("/status")
async def bot_status():
    return await bot.status()


@app.post("/command")
async def bot_command(message: dict):
    await bot.execute_command(message)
