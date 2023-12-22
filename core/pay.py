from aiogram import Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, ShippingOption, ShippingQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
# from core.queries.queries_for_shipping import my_ship


hog_shipping= ShippingOption(
    id='by',
    title='В Хогвартс',
    prices=[
        LabeledPrice(
            label='Доставка',
            amount=20000
        )
    ]
)

hell_shipping= ShippingOption(
    id='ru',
    title='В ад',
    prices=[
        LabeledPrice(
            label='Доставка в ад',
            amount=20000
        )
    ]
)


async def shipping_check(shipping_query: ShippingQuery, bot: Bot):
    shipping_options=[]
    countries=['ru', 'by']

    if shipping_query.shipping_address.country_code not in countries:
        return await bot.answer_shipping_query(shipping_query.id, ok=False, error_message='Не могу туда доставить...')
    
    if shipping_query.shipping_address.country_code=='by':
        shipping_options.append(hog_shipping)

    if shipping_query.shipping_address.country_code=='ru':
        shipping_options.append(hell_shipping)

    await bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options)

def get_pay_keyboard():

    pay_keyboard = InlineKeyboardBuilder()

    pay_keyboard.button(
        text='Оплатить',
        pay=True
    )

    pay_keyboard.button(
        text='Ссылка на доставщика',
        # url=my_ship.ship_company
    )

    pay_keyboard.adjust(1,1)

    return pay_keyboard.as_markup()



async def order(call: types.CallbackQuery, bot: Bot):
    print(call.message.chat.id)
    await bot.send_invoice(
        chat_id="-1001909523416",
        title='Оплата через тг-бот',
        description='Деньги за то, что я милый)',
        payload='Some interesting info',
        provider_token='381764678:TEST:73487',
        currency='rub',
        prices=[
            LabeledPrice(
                label='Сбор за милоту',
                amount=200000
            ),
            LabeledPrice(
                    label='скидка для вас',
                    amount=-180000
            ),
        ],
        max_tip_amount=100000,
        suggested_tip_amounts=[10000,20000,30000,50000], #max 4 параметра
        start_parameter="3334444opg",
        photo_url='https://gglot.com/wp-content/uploads/2021/01/Untitled-3-2-1024x576.jpg',
        photo_height=500,
        photo_size=150,
        photo_width=1000
    )


async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True)
    
async def successful_pay(message: Message):
    msg=f'Спасибки! {message.successful_payment.total_amount//100} {message.successful_payment.currency} - это большая сумма для маленького бота.'\
        f'\r\nyeeey!'
    await message.answer(msg)