from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import os
from core.config import ADMIN, CHANNEL
from core.utils.keyboards import get_kb
from core.utils.command import set_command
from core.database.functions import new_user_db, get_user_watch_status_db, upd_channel_msg_id, new_order_db, get_user_order
from core.utils.FSM import UserFSM, AdminFSM
from core.handlers.user_handlers import get_book, get_book2


def booking(a: bool):
    return a

base_router = Router(name="Main")


@base_router.startup()
async def start_bot(bot: Bot):
    await set_command(bot)
    await bot.send_message(chat_id=ADMIN, text="Bot started.")

@base_router.shutdown()
async def stop_bot(bot:Bot):
    await bot.send_message(ADMIN, "Bot stopped.")


@base_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()

    await new_user_db(message.from_user.id, message.from_user.username)
    await message.answer("Привет я бот для покупки/бронирования часов.")


    if str(message.from_user.id)==str(ADMIN):
        await message.answer("Отправьте сообщение с товаром")
        await state.set_state(AdminFSM.start)
        return

    await message.answer("Сейчас посмотрю, что вы бронировали.")
    
    user_watch = await get_user_watch_status_db(message.from_user.id)

    if user_watch=="no_order":
        await message.answer("Похоже вы ещё не забронировали ни одного товара. Перейдите в канал <a href='https://t.me/test_danya_channel'>Watch</a>, чтобы выбрать часы")
        return
    if user_watch=="bought":
        await message.answer("К сожалению выбранные вами часы уже куплены. Вы можете выбрать другие часы перейдя в канал <a href='https://t.me/test_danya_channel'>Watch</a>")
        return
    if user_watch=="booking":
        await message.answer("Данный товар в настоящее время бронируется другим покупателем. \
            Попробуйте забронировать через 5 минут или выберете другой товар")
    
    await state.set_state(UserFSM.start)
    await get_book(message=message, state=state, bot=bot)


@base_router.message(Command("book"))
async def cmd_book(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()

    await message.answer("Сейчас посмотрю, что вы бронировали.")
    
    user_watch = await get_user_watch_status_db(message.from_user.id)
    if user_watch=="no_order":
        await message.answer("Похоже вы ещё не забронировали ни одного товара. Перейдите в канал <a href='https://t.me/test_danya_channel'>Watch</a> и нажмите купить, чтобы выбрать часы")
        return
    if user_watch=="bought":
        await message.answer("К сожалению выбранные вами часы уже куплены. Вы можете выбрать другие часы перейдя в канал <a href='https://t.me/test_danya_channel'>Watch</a>")
        return
    if user_watch=="booking":
        await message.answer("Данный товар в настоящее время бронируется другим покупателем. \
            Попробуйте забронировать через 5 минут или выберете другой товар")
        return

    await state.set_state(UserFSM.start)
    await get_book(message=message, state=state, bot=bot)
    

@base_router.message(F.from_user.id==ADMIN)
async def get_other(message: types.Message, state: FSMContext):
    await message.answer("Чтобы отправить пост нажмите команду /start")

@base_router.callback_query(F.message.chat.id==int(CHANNEL))
async def book_from_channel(call: types.CallbackQuery, bot: Bot):
    # await upd_channel_msg_id(int(call.data), call.message.message_id)
    await call.answer("Товар выбран, перейдите в бота, чтобы купить его")
    is_new = await new_user_db(call.from_user.id, call.from_user.username)
    await new_order_db(call.from_user.id, int(call.data))

    if not(is_new):
        await bot.send_message(call.from_user.id, "Вы выбрали новый товар. Перейти к оплате?", reply_markup=get_kb({"Да": "yes_to_pay", "Нет": "no_to_pay"}, [2]))



@base_router.callback_query(F.data=="yes_to_pay")
async def call_book(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_reply_markup(reply_markup=None)
    await state.clear()

    await call.message.answer("Сейчас посмотрю, что вы бронировали.")
    
    user_watch = await get_user_watch_status_db(call.from_user.id)
    if user_watch=="no_order":
        await call.message.answer("Похоже вы ещё не забронировали ни одного товара. Перейдите в канал <a href='https://t.me/test_danya_channel'>Watch</a> и нажмите купить, чтобы выбрать часы")
        return
    if user_watch=="bought":
        await call.message.answer("К сожалению выбранные вами часы уже куплены. Вы можете выбрать другие часы перейдя в канал <a href='https://t.me/test_danya_channel'>Watch</a>")
        return
    if user_watch=="booking":
        await call.message.answer("Данный товар в настоящее время бронируется другим покупателем. \
            Попробуйте забронировать через 5 минут или выберете другой товар")
        return

    await state.set_state(UserFSM.start)
    await get_book2(call=call, state=state, bot=bot)

@base_router.callback_query(F.data=="no_to_pay")
async def no_to_pay(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await state.clear()  
