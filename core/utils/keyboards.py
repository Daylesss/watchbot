from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

def get_kb(buttons: dict, adjust: List[int]):
    kb= InlineKeyboardBuilder()
    for k, i in buttons.items():
        kb.button(text=str(k), callback_data=str(i))
    kb.adjust(*adjust)
    
    return kb.as_markup()
    # converter_kb.button(text='Плати', callback_data='Плати')
    # converter_kb.adjust(1)
    # return converter_kb.as_markup()
    
def get_book_kb(callback: str):
    kb= InlineKeyboardBuilder()
    kb.button(text="Бронировать", callback_data=f"book-{callback}", url="https://t.me/Develop4581_bot")
    kb.button(text="Купить", callback_data=f"buy-{callback}", url="https://t.me/Develop4581_bot")
    kb.adjust(1,1)
    return kb.as_markup()