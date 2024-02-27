import os
import logging
from aiogram import Bot, Router, types, F, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy import exc
from core.config import ADMIN, CHANNEL, CHANNEL_LINK
from core.utils.keyboards import get_kb, get_rep_kb
from core.utils.command import set_command
from core.database.functions import new_user_db, get_user_watch_status_db, new_order_db, add_admin_by_id, get_admins_id, get_admins_username, get_watch_status
from core.utils.FSM import UserFSM, AdminFSM
from core.handlers.user_handlers import get_book, get_book2
from core.handlers.admin_handl import parse_admins
# from core.handlers.user_handlers import user_router

util_router = Router()


base_router = Router(name="Main")

# @base_router.message()
# async def for_test(message: types.Message):
#     id = message.forward_from_chat
#     await message.answer(f"Отправлено  {id}")

@base_router.startup()
async def start_bot(bot: Bot):
    logging.info(f"Setting commands to bot")
    await set_command(bot)
    try:
        logging.info("Try to add an admin")
        await add_admin_by_id(tg_id=int(ADMIN))
    except exc.DBAPIError:
        logging.warning(f"Admin {int(ADMIN)} already exists")
    await bot.send_message(chat_id=ADMIN, text="Bot started.")

@base_router.shutdown()
async def stop_bot(bot:Bot):
    await bot.send_message(ADMIN, "Bot stopped.")

# @base_router.my_chat_member()
# async def m_ch_mem(message: types.ChatMember):
#     data = message.chat.id
#     logging.info(f"INVITED TO CHAT: {data}")
#     # print(data)

# @base_router.chat_member()
# async def ch_m(msg: types.ChatMember):
#     data = msg.chat.id
#     logging.info(f"INVITED TO CHAT: {data}")

@base_router.message(F.from_user.id==int(ADMIN), F.text=="Добавить администратора")
async def pre_add_admin(message: types.Message, state: FSMContext):
    logging.info("Add an administrator")
    await new_user_db(message.from_user.id, message.from_user.username)
    await state.clear()
    await state.set_state(AdminFSM.ADD)
    await message.answer(parse_admins(await get_admins_username()))
    await message.answer(f"Введите имя пользователя которого хотите сделать админом. Внимание, этот пользователь должен взаимодействовать с ботом до этого хотя бы раз. \n Например: {message.from_user.username}")


@base_router.message(F.from_user.id==int(ADMIN), F.text=="Удалить администратора")
async def pre_remove_admin(message: types.Message, state: FSMContext):
    logging.info("Remove an administrator")
    await new_user_db(message.from_user.id, message.from_user.username)
    await state.clear()
    await state.set_state(AdminFSM.REMOVE)
    await message.answer(parse_admins(await get_admins_username()))
    await message.answer(f"Введите имя пользователя которого исключить из списка админов.  \n Например: {message.from_user.username}")

@base_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext, bot: Bot):
    logging.info(f"START {message.from_user.id}")
    await state.clear()
    #res = await get_watch_status(6)
   # print(str(res), flush = True)


    await new_user_db(message.from_user.id, message.from_user.username)
    await message.answer("Привет я бот для покупки/бронирования часов.")
    
    admins = await get_admins_id()



    if int(message.from_user.id) in admins:
        if str(message.from_user.id)==ADMIN:
            # buttons = ["add_admin","remove_admin"]
            kb = get_rep_kb(is_main=True)
        else:
            kb = get_rep_kb(is_main=False)
        await message.answer("Отправьте сообщение с товаром", reply_markup=kb)
        await state.set_state(AdminFSM.start)
        await state.update_data(unique_id=f"{message.from_user.id}{message.message_id}")
        return

    await message.answer("Сейчас посмотрю, что вы бронировали.")
    logging.info(f"Checking orders of user {message.from_user.id}")
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
        return
    
    await state.set_state(UserFSM.start)
    await get_book(message=message, state=state, bot=bot)


@base_router.message(Command("book"))
async def cmd_book(message: types.Message, state: FSMContext, bot: Bot):
    logging.info(f"BOOK {message.from_user.id}")
    await state.clear()
    await new_user_db(message.from_user.id, message.from_user.username)

    await message.answer("Сейчас посмотрю, что вы бронировали.")
    logging.info(f"Check user order  {message.from_user.id}")
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


@base_router.message(F.text=="Отправить пост")
async def send_adm_post(message: types.Message, state: FSMContext):
    logging.info(f"Try to send new post {message.from_user.id}")
    await new_user_db(message.from_user.id, message.from_user.username)
    await state.clear()
    admins = await get_admins_id()



    if int(message.from_user.id) in admins:
        logging.info(f"user {message.from_user.id} is admin")
        if str(message.from_user.id)==ADMIN:
            kb = get_rep_kb(is_main=True)
        else:
            kb = get_rep_kb(is_main=False)
        await message.answer("Отправьте сообщение с товаром", reply_markup=kb)
        await state.set_state(AdminFSM.start)
        await state.update_data(unique_id=f"{message.from_user.id}{message.message_id}")
        return
    logging.warning(f"user {message.from_user.id} is not admin")

@base_router.message(F.text=="LOGS")
async def send_adm_post(message: types.Message, state: FSMContext):
    logging.info(f"Getting logs {message.from_user.id}")
    await new_user_db(message.from_user.id, message.from_user.username)
    await state.clear()
    admins = await get_admins_id()



    if int(message.from_user.id) in admins:
        if str(message.from_user.id)==ADMIN:
            kb = get_rep_kb(is_main=True)
        else:
            kb = get_rep_kb(is_main=False)
        
        await message.answer_document(types.input_file.FSInputFile("logs/py_log.log"))
    logging.warning(f"user {message.from_user.id} is not admin")

@base_router.callback_query(F.message.chat.id==int(CHANNEL))
async def book_from_channel(call: types.CallbackQuery, bot: Bot):
    logging.info(f"User {call.from_user.id} choose watch {call.data}")
    await new_user_db(call.from_user.id, call.from_user.username)
    await call.answer("Товар выбран, перейдите в бота, чтобы купить его")
    is_new = await new_user_db(call.from_user.id, call.from_user.username)
    await new_order_db(call.from_user.id, int(call.data))

    if not(is_new):
        try:
            await bot.send_message(call.from_user.id, "Вы выбрали новый товар. Перейти к оплате?", reply_markup=get_kb({"Да": "yes_to_pay", "Нет": "no_to_pay"}, [2]))
        except TelegramForbiddenError as err:
            logging.warning(f"Can not send message to user that exists in db {err}")



@base_router.callback_query(F.data=="yes_to_pay")
async def call_book(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_reply_markup(reply_markup=None)
    await state.clear()

    await call.message.answer("Сейчас посмотрю, что вы бронировали.")
    logging.info(f"Check user order  {call.from_user.id}")
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
    logging.info(f"no to pay {call.from_user.id}")
    await call.message.edit_reply_markup(reply_markup=None)
    await state.clear()  

