from aiohttp import ClientSession, ClientTimeout
import hashlib
import os
import json
import asyncio
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from core.config import ADMIN, CHANNEL, WEBHOOK, SECRET, CHANNEL_LINK
from core.utils.keyboards import get_kb, get_book_kb
from core.utils.FSM import UserFSM
from core.database.functions import get_channel_message, set_pay_params_db, upd_watch_book_status_db
from core.database.functions import get_watch_id, get_ch_msg_db, get_watch_status, get_user_order

def parse_order(username: str, order: tuple):
    if order[0]=="book":
        book = "ЗАБРОНИРОВАЛ"
    else:
        book = "КУПИЛ"
    
    return f"Пользователь: @{username} \n{book} следующий товар за {order[1]} USD:"

    

async def send_qr(call: types.CallbackQuery, state: FSMContext, bot: Bot, data:dict):
    watch_id = await get_watch_id(call.from_user.id)
    msg = await get_ch_msg_db(watch_id)
    await bot.edit_message_reply_markup(chat_id=CHANNEL,message_id=msg, reply_markup=None)
    is_for_sale = await upd_watch_book_status_db(call.from_user.id, watch_id)
    if not(is_for_sale):
        await state.clear()
        await call.message.answer("извините, данный товар в настоящий момент бронируется другим человеком. Попробуйте через пять минут или выберете другой товар.")
        return
    await state.set_state(UserFSM.pay)
    qrcd = data.get("qrCode")
    font_path = r"DejaVuSansMono.ttf"  
    font_size = 24
    font = ImageFont.truetype(font_path, font_size)
    img = Image.new('RGB', (580, 550), color=(255,255,255))
    d = ImageDraw.Draw(img)
    d.text((0, 0), qrcd, font=font, fill=(0, 0, 0))
    qr_name = f"static/qr_{call.from_user.id}.png"
    img.save(qr_name)
    file = types.FSInputFile(qr_name)
    # with open(qr_name, "rb") as f:
    qr = await call.message.answer_photo(file)
    
    await call.message.answer("Если через пять минут не приходит ответа, сообщение с qr кодом удаляется.")
    is_bought = False
    for i in range(60):
        await asyncio.sleep(5) 
        if await get_watch_status(watch_id)=="Done":
            is_bought = True
            break

    os.remove(qr_name)
    if not(is_bought):
        await qr.delete()
        await upd_watch_book_status_db(tg_id=call.from_user.id, watch_id=watch_id, old_status="booking", new_status="for_sale", order_none=True)
        await bot.edit_message_reply_markup(chat_id=CHANNEL,message_id=msg, reply_markup=get_book_kb(watch_id))
        await call.message.answer("Время для оплаты истекло")
        await state.clear()
        return

    await qr.delete()
    await state.clear()
    order = await get_user_order(watch_id)
    await bot.send_message(ADMIN, parse_order(call.from_user.username, order))
    await bot.copy_message(ADMIN, CHANNEL, order[2], reply_markup=None)
    await call.message.answer("Товар успешно оплачен. Администратору уже отправлено сообщение.")


user_router = Router()

async def get_book(message: types.Message, state: FSMContext, bot: Bot):
    
    book_msg = await get_channel_message(message.from_user.id)
    
    await bot.copy_message(message.from_user.id, CHANNEL, book_msg, reply_markup=None)

    buttons = {
        "Бронировать": "book",
        "Купить": "buy",
        "Отмена": "no_buy"
    }

    keyboard = get_kb(buttons=buttons, adjust=[1,1,1])
    await message.answer("Хотите купить или забронировать данный товар?", reply_markup=keyboard)

async def get_book2(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    
    book_msg = await get_channel_message(call.from_user.id)
    
    await bot.copy_message(call.from_user.id, CHANNEL, book_msg, reply_markup=None)

    buttons = {
        "Бронировать": "book",
        "Купить": "buy",
        "Отмена": "no_buy"
    }

    keyboard = get_kb(buttons=buttons, adjust=[1,1,1])
    await call.message.answer("Хотите купить или забронировать данный товар?", reply_markup=keyboard)

@user_router.callback_query(UserFSM.start, F.data=="no_buy")
async def no_buy(call: types.CallbackQuery, state: FSMContext):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await state.clear()
    
    await call.message.answer(f"Хорошо. Другие товары вы можете найти на канале <a href='{CHANNEL_LINK}'>Watch</a>. \
Чтобы снова вернуться к бронированию или покупке, используйте команду book")

@user_router.callback_query(UserFSM.start, F.data=="book")
@user_router.callback_query(UserFSM.start, F.data=="buy")
async def yes_buy(call: types.CallbackQuery, state: FSMContext):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await state.set_state(UserFSM.network)
    await state.update_data(book_or_buy=call.data)
    
    buttons = {
        "trc20": "trc20",
        "erc20": "erc20"
    }
    
    keyboard = get_kb(buttons, [2])
    
    await call.message.answer("Выберете сеть для оплаты", reply_markup=keyboard)

@user_router.callback_query(UserFSM.network, F.data=="trc20")
@user_router.callback_query(UserFSM.network, F.data=="erc20")
async def network(call: types.CallbackQuery, state: FSMContext):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await state.update_data(network = call.data)
    
    await state.set_state(UserFSM.address)
    await call.message.answer("Принято. Теперь введите адресс кошелька.")

def pay_data_conv(data: dict):
    if data["book_or_buy"]=="buy":
        bob = "бронь"
    if data["book_or_buy"]=="book":
        bob = "покупка"
    msg = f'''Проверьте правильность введенных данных:
Покупка/бронирование - {bob}
Сеть - {data["network"]}
адрес - {data['address']}
Цена - {data["price"]} USD

После подтверждения у вас будет пять минут на то, чтобы оплатить товар. По истечении времени оплата будет недействительна.'''
    return msg

@user_router.message(UserFSM.address, F.text.isalnum())
async def address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    price = await set_pay_params_db(message.from_user.id, data)
    await state.update_data(price = price)
    data["price"] = price
    buttons = {
        "Продолжить": "continue_book",
        "Изменить": "cancel_book"
    }
    keyboard = get_kb(buttons, [1,1])
    await state.set_state(UserFSM.confirm)
    await message.answer(pay_data_conv(data), reply_markup=keyboard)

def make_hash(data: dict, tg_id: int):
    hash_dict2 = {
    "payerAddress": data["address"],
    "amount": data["price"],
    "network": data["network"],
    "webhookUrl": str(WEBHOOK+str(tg_id)),
    "payment_type": "investment",
    }
    hash_list = list(hash_dict2.keys())
    hash_list = sorted(hash_list)
    hash_str = "".join(str(hash_dict2[i]) for i in hash_list)+SECRET

    hash = hashlib.md5(hash_str.encode()).hexdigest()
    return {
    "payerAddress": data["address"],
    "amount": data["price"],
    "network": data["network"],
    "webhookUrl": str(WEBHOOK+str(tg_id)),
    "payment_type": "investment",
    "hash": hash
    }

@user_router.callback_query(UserFSM.confirm, F.data=="cancel_book")
async def cancel_book(call: types.CallbackQuery, state: FSMContext):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await state.clear()
    await call.message.answer("Нажмите /book чтобы ввести данные занаво")

@user_router.callback_query(UserFSM.confirm, F.data=="continue_book")
async def address(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await call.message.answer("Высылаю qrcode для оплаты")
    await state.set_state(UserFSM.qr)
    
    data = await state.get_data()

    data_new = make_hash(data, call.from_user.id)
    
    print(data_new)

    timeout = ClientTimeout(total=30)
    
    async with ClientSession(timeout=timeout) as session:
        resp = await session.post("http://78.40.216.26:3001/payment", json=data_new)
        statusCode = resp.status
        resp = await resp.json()
    
    if int(statusCode)==201: #200
        await send_qr(call, state, bot, resp)
        return
    elif int(statusCode)==403:
        await call.message.answer("Ненадежный адрес. Введите другой адрес")
        await state.set_state(UserFSM.address)
        return
    else:
        await state.clear()
        await call.message.answer("Что-то пошло не так попробуйте ввести другой адрес или воспользуйтесь командой /book")

