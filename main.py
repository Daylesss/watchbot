from aiogram import Bot, Dispatcher
from aiogram import types
import asyncio
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from core.config import BOT_TOKEN
# from core.pay import order, pre_checkout_query, successful_pay, shipping_check
# def get_in_convert_kb():
#     converter_kb= InlineKeyboardBuilder()
#     converter_kb.button(text='Начать конвертировать', callback_data='conv_start')
#     converter_kb.adjust(1)
#     return converter_kb.as_markup()

# def get_pay_kb():
#     converter_kb= InlineKeyboardBuilder()
#     converter_kb.button(text='Плати', callback_data='Плати')
#     converter_kb.adjust(1)
#     return converter_kb.as_markup()

# async def start_bot(bot: Bot):
#     await bot.send_message(chat_id="-1001909523416", text="Hello world", reply_markup=get_in_convert_kb())

# async def test_mes(call: types.CallbackQuery, bot: Bot):
#     await bot.send_message(chat_id="-1001909523416", text="ПРИВЕТ МИР", reply_markup=get_in_convert_kb()) #"-1001909523416"
#     await call.message.answer("Плати", reply_markup=get_pay_kb())

# async def admin(message: types.Message, bot: Bot):
#     await bot.send_message(chat_id="-1001909523416", text="Админ лох")
from core.handlers.base_handlers import base_router
from core.handlers.admin_handl import admin_router
from core.handlers.user_handlers import user_router

async def main():
    bot=Bot(token=BOT_TOKEN, parse_mode='HTML')
    logging.basicConfig(level=logging.INFO)
    
    dp=Dispatcher()
    
    # dp.startup.register(start_bot)
    # dp.channel_post.register(admin, F.text == "лох")
    # dp.callback_query.register(order, F.data=='Плати')
    # dp.callback_query.register(test_mes)
    # dp.message.register(successful_pay, F.successful_payment)
    # dp.pre_checkout_query.register(pre_checkout_query)
    dp.include_routers(base_router, admin_router, user_router)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as ex:
        logging.error(f'[!!! EXCEPTION] - {ex}', exc_info=True)
    finally:
        await bot.session.close()


if __name__=="__main__":
    asyncio.run(main())