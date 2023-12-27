from aiohttp import ClientSession, ClientTimeout
import json
from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from core.config import ADMIN, CHANNEL
from core.utils.keyboards import get_kb
from core.utils.FSM import UserFSM

def get_book_db(tg_id: int):
    return "1234"

def is_booked_db(tg_id: int):
    return False

def book_or_buy_db(tg_id):
    return 1

def buy_db(tg_id: int):
    print("куплено в базе")

async def send_qr(message: types.Message, state: FSMContext):
    await state.set_state(UserFSM.pay)
    #здесь идет поллинг бд
    await message.answer("Здесь присылается QRcode")
    print("QRRRRRRRRRRR")


user_router = Router()

async def get_book(message: types.Message, state: FSMContext, bot: Bot):
    
    book_msg = get_book_db(message.from_user.id)
    
    if is_booked_db(message.from_user.id):
        await message.answer("Извините товар уже зарезервирован")
        return
    
    # await bot.copy_message(message.from_user.id, ADMIN, book_msg)
    print("сообщение")

    buttons = {
        "Да": "yes_buy",
        "Нет": "no_buy"
    }
    keyboard = get_kb(buttons=buttons, adjust=[2])
    if book_or_buy_db(2):
        await message.answer("Хотите купить данный товар?", reply_markup=keyboard)
    
    else:
        await message.answer("Хотите забронировать данный товар?", reply_markup=keyboard)

@user_router.callback_query(UserFSM.start, F.data=="no_buy")
async def no_buy(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    await call.message.answer("Хорошо. Другие товары вы можете найти на канале 'канал'. \
                              Чтобы снова вернуться к бронированию или покупке, используйте команду book")

@user_router.callback_query(UserFSM.start, F.data=="yes_buy")
async def yes_buy(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserFSM.network)
    
    buttons = {
        "trc20": "trc20",
        "erc20": "erc20"
    }
    
    keyboard = get_kb(buttons, [2])
    
    await call.message.answer("Выберете сеть для оплаты", reply_markup=keyboard)

@user_router.callback_query(UserFSM.network, F.data=="trc20" or F.data=="erc20")
async def network(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(network = call.data)
    
    await state.set_state(UserFSM.address)
    await call.message.answer("Принято. Теперь введите адресс кошелька.")


@user_router.message(UserFSM.address, F.text)
async def address(message: types.Message, state: FSMContext):
    await message.answer("Высылаю ссылку для оплаты")
    
    await state.set_state(UserFSM.qr)

    params = {
    "id": "string",
    "payerAddress": message.text,
    "amount": 100,
    "network": "erc20",
    "webhookUrl": "https://webhook.site/9a6543b8-8016-47c3-96f4-85c4c4c63524",
    "payment_type": "purchase",
    "hash": "32a8344e273b9fdb404391c770f69173"
    }

    timeout = ClientTimeout(total=30)
    
    async with ClientSession(timeout=timeout) as session:
        resp =await session.post("http://78.40.216.26:3001/payment", data=json.dumps(params))
    
    resp = await resp.json()
    
    if int(resp["statusCode"])==403: #200
        await send_qr(message, state)
        return
    elif int(resp["statusCode"])==403:
        await message.answer("Ненадежный адрес. Введите другой адрес")
        await state.set_state(UserFSM.address)
        return
    else:
        await message.answer("Что-то пошло не так попробуйте ввести другой адрес или воспользуйтесь командой /book")
    
    print(resp)

