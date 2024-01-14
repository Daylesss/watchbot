from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class UserFSM(StatesGroup):
    start = State()
    network = State()
    address = State()
    confirm = State()
    qr = State()
    pay = State()


class AdminFSM(StatesGroup):
    start = State()
    text = State()
    price = State()
    price2= State()
    name = State()
    check = State()
    ADD = State()
    REMOVE = State()
