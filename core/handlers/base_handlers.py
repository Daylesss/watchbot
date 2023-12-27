from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import os
from core.config import ADMIN, CHANNEL
from core.utils.command import set_command
from core.database.database import async_session_maker
from sqlalchemy import select, insert
from core.database.models import user
from core.database.functions import new_user_db
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.FSM import UserFSM, AdminFSM
from core.handlers.user_handlers import get_book


def booking(a: bool):
    return a

base_router = Router(name="Main")

def get_pay_kb():
    converter_kb= InlineKeyboardBuilder()
    converter_kb.button(text='Плати', callback_data='Плати', url="https://t.me/Develop4581_bot")
    converter_kb.adjust(1)
    return converter_kb.as_markup()

@base_router.startup()
async def start_bot(bot: Bot):
    await set_command(bot)
    await bot.send_message(chat_id=CHANNEL, text="Courses bot started.", reply_markup=get_pay_kb())

@base_router.shutdown()
async def stop_bot(bot:Bot):
    await bot.send_message(ADMIN, "Courses bot stopped.")


@base_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()

    await new_user_db(message.from_user.id, message.from_user.username)
    await message.answer("Привет я бот для покупки/бронирования часов.")


    if str(message.from_user.id)==str(ADMIN):
        await message.answer("Отправьте сообщение с товаром")
        await state.set_state(AdminFSM.start)
        return
    if not(booking(True)):
        await message.answer("Похоже вы ещё не забронировали ни одного товара. Перейдите в канал 'название канала', чтобы выбрать часы")
        return

    await message.answer("Сейчас посмотрю, что вы бронировали.")
    await state.set_state(UserFSM.start)
    await get_book(message=message, state=state, bot=bot)

@base_router.message(F.from_user.id==ADMIN)
async def get_other(message: types.Message, state: FSMContext):
    await message.answer("Чтобы отправить пост нажмите команду start")


# @base_router.callback_query()
# async def test_db(call: types.CallbackQuery):
#     # print(call.from_user.id)
#     call.
#     await new_user(call.from_user.id, call.from_user.username)
#     print("Все")