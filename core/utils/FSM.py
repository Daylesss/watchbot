from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class UserFSM(StatesGroup):
    start = State()
    network = State()
    address = State()
    qr = State()
    pay = State()


class AdminFSM(StatesGroup):
    start = State()
    price = State()
    name = State()
    check = State()
