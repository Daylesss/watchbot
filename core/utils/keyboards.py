from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from core.config import BOT_LINK

def get_kb(buttons: dict, adjust: List[int]):
    kb= InlineKeyboardBuilder()
    for k, i in buttons.items():
        kb.button(text=str(k), callback_data=str(i))
    kb.adjust(*adjust)
    
    return kb.as_markup()
    # converter_kb.button(text='Плати', callback_data='Плати')
    # converter_kb.adjust(1)
    # return converter_kb.as_markup()
    
def get_book_kb(watch_id: str):
    kb= InlineKeyboardBuilder()
    kb.button(text="Купить", callback_data=f"{watch_id}")#, url=BOT_LINK)
    kb.button(text="Продолжить в боте", url=BOT_LINK)
    kb.adjust(1,1)
    return kb.as_markup()