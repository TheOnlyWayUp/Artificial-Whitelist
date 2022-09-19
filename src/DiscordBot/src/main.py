import uvicorn
from api import app
from bot import bot
from threading import Thread
from config import API_CONFIG, BOT_CONFIG


def run_api():
    uvicorn.run(
        app, host=API_CONFIG["bind"]["address"], port=API_CONFIG["bind"]["port"]
    )


def run_bot():
    bot.run(BOT_CONFIG["token"])


if __name__ == "__main__":
    api_thread = Thread(target=run_api)
    api_thread.start()
    run_bot()
