from aiogram import Bot, Dispatcher
from aiogram import types
import asyncio
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from core.config import BOT_TOKEN
from core.handlers.base_handlers import base_router, util_router
from core.handlers.admin_handl import admin_router
from core.handlers.user_handlers import user_router

async def main():
    bot=Bot(token=BOT_TOKEN, parse_mode='HTML')
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(filename = "logs/py_log.log")]
        )
    
    dp=Dispatcher()

    dp.include_routers(base_router, admin_router, user_router, util_router)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as ex:
        logging.error(f'[!!! EXCEPTION] - {ex}', exc_info=True)
    finally:
        await bot.session.close()


if __name__=="__main__":
    asyncio.run(main())