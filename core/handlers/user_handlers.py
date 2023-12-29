from aiohttp import ClientSession, ClientTimeout
import json
import asyncio
from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from core.config import ADMIN, CHANNEL
from core.utils.keyboards import get_kb, get_book_kb
from core.utils.FSM import UserFSM
from core.database.functions import get_channel_message, set_pay_params_db, upd_watch_book_status_db, get_watch_id, get_ch_msg_db

def get_book_db(tg_id: int):
    return "1234"

def is_booked_db(tg_id: int):
    return False

def book_or_buy_db(tg_id):
    return 1

def buy_db(tg_id: int):
    print("куплено в базе")

async def send_qr(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    watch_id = await get_watch_id(call.from_user.id)
    msg = await get_ch_msg_db(watch_id)
    await bot.edit_message_reply_markup(chat_id=CHANNEL,message_id=msg, reply_markup=None)
    await upd_watch_book_status_db(call.from_user.id, watch_id)
    await state.set_state(UserFSM.pay)
    #здесь идет поллинг бд
    qr = await call.message.answer("Здесь присылается QRcode. Далее идет поллинг сервера в ожидании ответа об оплате")
    await call.message.answer("Если через пять минут не приходит ответа, сообщение с qr кодом удаляется.")
    await asyncio.sleep(300) 
    await qr.delete()
    await upd_watch_book_status_db(tg_id=call.from_user.id,watch_id=watch_id, status="for_sale", order_none=True)
    await bot.edit_message_reply_markup(chat_id=CHANNEL,message_id=msg, reply_markup=get_book_kb(msg))


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

@user_router.callback_query(UserFSM.start, F.data=="no_buy")
async def no_buy(call: types.CallbackQuery, state: FSMContext):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await state.clear()
    
    await call.message.answer("Хорошо. Другие товары вы можете найти на канале 'канал'. \
                              Чтобы снова вернуться к бронированию или покупке, используйте команду book")

@user_router.callback_query(UserFSM.start, F.data=="book")
@user_router.callback_query(UserFSM.start, F.data=="buy")
async def yes_buy(call: types.CallbackQuery, state: FSMContext):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await state.set_state(UserFSM.network)
    await state.update_data(book_or_buy="book")
    
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
    Цена - {data["price"]} USD'''
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
    await call.message.answer("Высылаю ссылку для оплаты")
    await state.set_state(UserFSM.qr)
    
    data = await state.get_data()

    params = {
    "id": "string",
    "payerAddress": data["address"],
    "amount": data["price"],
    "network": data["network"],
    "webhookUrl": "https://webhook.site/9a6543b8-8016-47c3-96f4-85c4c4c63524",
    "payment_type": "purchase",
    "hash": "32a8344e273b9fdb404391c770f69173"
    }

    timeout = ClientTimeout(total=30)
    
    async with ClientSession(timeout=timeout) as session:
        resp = await session.post("http://78.40.216.26:3001/payment", data=json.dumps(params))
    
    resp = await resp.json()
    
    if int(resp["statusCode"])==403: #200
        await send_qr(call, state, bot)
        return
    elif int(resp["statusCode"])==403:
        await call.message.answer("Ненадежный адрес. Введите другой адрес")
        await state.set_state(UserFSM.address)
        return
    else:
        await state.clear()
        await call.message.answer("Что-то пошло не так попробуйте ввести другой адрес или воспользуйтесь командой /book")
    
    print(resp)

