from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from core.config import ADMIN, CHANNEL
# from core.database.database import async_session_maker
from core.utils.FSM import AdminFSM
from core.utils.keyboards import get_kb, get_book_kb

def validate_price(price):
    return True

def add_watch(data):
    print("Товар добавлен")

def get_callback():
    return "123"

admin_router = Router()


@admin_router.message(F.from_user.id==int(ADMIN),AdminFSM.start)
async def get_channel_post(message: types.Message, state: FSMContext):
    await state.update_data(message = message.message_id)
    
    await message.answer("Записал, введите цену  в ддолларах целым числом." )
    await state.set_state(AdminFSM.price)

@admin_router.message(F.from_user.id==int(ADMIN), AdminFSM.price, F.text)
async def get_price(message: types.Message, state: FSMContext):
    is_price = validate_price(message.text)
    if not(is_price):
        await message.answer("Неправильная цена. Введите цену ещё раз")
        return

    await state.update_data(price =message.text)
    await message.answer("Принято. Введите название")
    await state.set_state(AdminFSM.name)


async def check_post(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    add_watch(data)


    callback = get_callback()
    await state.update_data(callback = callback)
    
    keyboard = get_book_kb(callback)
    # buttons = {
    #     "Бронировать": callback
    # }
    # keyboard = get_kb(buttons, [1]
    await bot.copy_message(message.from_user.id, message.from_user.id, data['message'], reply_markup=keyboard)
    
    await state.set_state(AdminFSM.check)
    await message.answer("Отправить данное сообщение?", reply_markup=get_kb({"Отправить": "yes_post", "Не отправлять": "no_post"}, [2]))


@admin_router.message(F.from_user.id==int(ADMIN), AdminFSM.name, F.text)
async def get_name(message: types.Message, state: FSMContext, bot: Bot):
    # is_price = validatenprice(message.text)
    # if not(is_price):
    #     await message.answer("Неправильная цена. Введите цену ещё раз")
    #     return


    await state.update_data(price =message.text)
    await message.answer("Принято")
    await check_post(message, state, bot)

@admin_router.callback_query(F.from_user.id==int(ADMIN), AdminFSM.check, F.data=="yes_post")
async def send_post(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    keyboard = get_book_kb(data['callback'])
    await bot.copy_message(CHANNEL, call.from_user.id, data['message'], reply_markup=keyboard)
    await call.message.answer("Сообщение отправлено")




