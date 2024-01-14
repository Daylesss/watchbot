from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import os
from core.config import ADMIN, CHANNEL, CHANNEL_LINK
from core.utils.keyboards import get_kb, get_rep_kb
from core.utils.command import set_command
from core.database.functions import new_user_db, get_user_watch_status_db, new_order_db, add_admin_by_id, get_admins_id, get_watch_files_watch
from core.utils.FSM import UserFSM, AdminFSM
from core.handlers.user_handlers import get_book, get_book2
from core.handlers.admin_handl import get_channel_post
# from core.handlers.user_handlers import user_router

util_router = Router()

def booking(a: bool):
    return a

base_router = Router(name="Main")


# @base_router.message()
# async def for_test(message: types.Message):
#     id = message.forward_from_chat
#     await message.answer(f"Отправлено  {id}")

@base_router.startup()
async def start_bot(bot: Bot):
    await set_command(bot)
    try:
        await add_admin_by_id(tg_id=int(ADMIN))
    except:
        print("Admin already exists")
    await bot.send_message(chat_id=ADMIN, text="Bot `started.`", parse_mode="MarkDown")

@base_router.shutdown()
async def stop_bot(bot:Bot):
    await bot.send_message(ADMIN, "Bot stopped.")


@base_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    


    await new_user_db(message.from_user.id, message.from_user.username)
    await message.answer("Привет я бот для покупки/бронирования часов.")
    
    admins = await get_admins_id()



    if int(message.from_user.id) in admins:
        if str(message.from_user.id)==ADMIN:
            # buttons = ["add_admin","remove_admin"]
            kb = get_rep_kb()
        else:
            kb = None
        await message.answer("Отправьте сообщение с товаром", reply_markup=kb)
        await state.set_state(AdminFSM.start)
        await state.update_data(unique_id=f"{message.from_user.id}{message.message_id}")
        return

    await message.answer("Сейчас посмотрю, что вы бронировали.")
    
    user_watch = await get_user_watch_status_db(message.from_user.id)

    if user_watch=="no_order":
        await message.answer(f"Похоже вы ещё не забронировали ни одного товара. Перейдите в канал <a href='{CHANNEL_LINK}'>Watch</a>, чтобы выбрать часы")
        return
    if user_watch=="bought":
        await message.answer(f"К сожалению выбранные вами часы уже куплены. Вы можете выбрать другие часы перейдя в канал <a href='{CHANNEL_LINK}'>Watch</a>")
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
        await message.answer(f"Похоже вы ещё не забронировали ни одного товара. Перейдите в канал <a href='{CHANNEL_LINK}'>Watch</a> и нажмите купить, чтобы выбрать часы")
        return
    if user_watch=="bought":
        await message.answer(f"К сожалению выбранные вами часы уже куплены. Вы можете выбрать другие часы перейдя в канал <a href='{CHANNEL_LINK}'>Watch</a>")
        return
    if user_watch=="booking":
        await message.answer("Данный товар в настоящее время бронируется другим покупателем. \
            Попробуйте забронировать через 5 минут или выберете другой товар")
        return

    await state.set_state(UserFSM.start)
    await get_book(message=message, state=state, bot=bot)


@util_router.message(F.text=="add_post")
async def get_other(message: types.Message, state: FSMContext):
    await state.clear()
    admins = await get_admins_id()



    if int(message.from_user.id) in admins:
        if str(message.from_user.id)==ADMIN:
            # buttons = ["add_admin","remove_admin"]
            kb = get_rep_kb()
        else:
            kb = None
        await message.answer("Отправьте сообщение с товаром", reply_markup=kb)
        await state.set_state(AdminFSM.start)
        await state.update_data(unique_id=f"{message.from_user.id}{message.message_id}")
        return

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
        await call.message.answer(f"Похоже вы ещё не забронировали ни одного товара. Перейдите в канал <a href='{CHANNEL_LINK}'>Watch</a> и нажмите купить, чтобы выбрать часы")
        return
    if user_watch=="bought":
        await call.message.answer(f"К сожалению выбранные вами часы уже куплены. Вы можете выбрать другие часы перейдя в канал <a href='{CHANNEL_LINK}'>Watch</a>")
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

