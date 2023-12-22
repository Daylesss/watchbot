from aiogram import Bot, Dispatcher, types
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.webhook import SendMessage

from fastapi import FastAPI, Request, HTTPException

API_TOKEN = "YOUR_TELEGRAM_BOT_API_TOKEN"
WEBHOOK_URL = "https://your_domain.com/telegram_webhook_path"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()

# Устанавливаем webhook для бота
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

# Обработчик входящих сообщений

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

# FastAPI endpoint для обработки запросов от Telegram
@app.post("/telegram_webhook_path")
async def telegram_webhook(request: Request):
    if request.headers.get("content-type") == "application/json":
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.process_update([update])
        return {"ok": True}
    else:
        raise HTTPException(status_code=415, detail="Unsupported Media Type")

# Устанавливаем логгирование
# dp.middleware.setup(LoggingMiddleware())

# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
