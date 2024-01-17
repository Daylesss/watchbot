from aiogram import Bot, Router, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaAudio, InputMediaPhoto, InputMediaVideo, InputMediaDocument
from core.config import ADMIN, CHANNEL
from core.utils.FSM import AdminFSM
from core.utils.keyboards import get_kb, get_book_kb
from core.database.functions import insert_watch_db, upd_channel_msg_id, get_admins_username
from core.database.functions import  exist_user_by_username, add_admin, delete_admin, insert_watch_media
from core.database.functions import get_watch_files_unique, insert_watch_file, get_watch_files_watch
from core.database.functions import get_watch_txt, get_user_by_username



admin_router = Router()


@admin_router.message(AdminFSM.start)
async def get_channel_post(message: types.Message, state: FSMContext):
    
    data = await state.get_data()
    # data_size = len(data.keys())
    unique_id = data.get("unique_id", False)
    # if not(unique_id):
    #     await state.update_data(unique_id = f"{message.from_user.id}{message.message_id}")
    #     if (message.caption or message.text):
    #         await state.update_data(message_id = message.message_id)
    #         await message.answer("Записал, введите цену ПОКУПКИ в долларах целым числом." )
    #         await state.set_state(AdminFSM.price)
    #         return
    #     if message.video:
    #         file_id = message.video.file_id
    #         file_type = "video"
    #     elif message.photo:
    #         file_id = message.photo[-1].file_id
    #         file_type = "photo"
    #     elif message.audio:
    #         file_id = message.audio.file_id
    #         file_type = "audio"
    #     elif message.document:
    #         file_id = message.document.file_id
    #         file_type = "document"
    #     else:
    #         return
    #     await insert_watch_file(unique_id = f"{message.from_user.id}{message.message_id}", file_id=file_id, file_type=file_type)
    #     return

    if message.text == "CANCEL":
        await state.clear()
        await message.answer("Предыдущие сообщения не будут записаны")
        return

    if message.text =="END":
        await state.set_state(AdminFSM.text)
        await message.answer("Введите текст сообщения")
        return
    if message.text:
        await state.update_data(message_text = message.text)
    
        await message.answer("Записал, введите цену ПОКУПКИ в долларах целым числом." )
        await state.set_state(AdminFSM.price)
        return
        
    num_files = len(await get_watch_files_unique(unique_id))
    if num_files==10:
        await state.set_state(AdminFSM.text)
        await message.answer("Введите текст сообщения")
        return
    
    if message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    else:
        return
    await insert_watch_file(unique_id = unique_id, file_id=file_id, file_type=file_type)


@admin_router.message(AdminFSM.text, F.text)
async def get_channel__text(message: types.Message, state: FSMContext):
    await state.update_data(message_text = message.text)
    
    await message.answer("Записал, введите цену ПОКУПКИ в долларах целым числом." )
    await state.set_state(AdminFSM.price)

@admin_router.message(AdminFSM.price, F.text)
async def get_price(message: types.Message, state: FSMContext):

    if not(message.text.isdigit()):
        await message.answer("Неправильная цена. Введите цену ещё раз")
        return
    if message.text=="0":
        await message.answer("Цена не может быть меньше единицы. Введите цену ещё раз")
        return
    await state.update_data(price =message.text)
    await message.answer("Принято. Введите цену БРОНИРОВАНИЯ в долларах целым числом.")
    await state.set_state(AdminFSM.price2)

@admin_router.message(AdminFSM.price2, F.text)
async def get_price2(message: types.Message, state: FSMContext):

    if not(message.text.isdigit()):
        await message.answer("Неправильная цена. Введите цену ещё раз")
        return
    if message.text=="0":
        await message.answer("Цена не может быть меньше единицы. Введите цену ещё раз")
        return
    await state.update_data(price2 =message.text)
    await message.answer("Принято. Введите название")
    await state.set_state(AdminFSM.name)

async def get_files(watch_id):
    files_and_types = await get_watch_files_watch(watch_id)
    files = []
    caption = await get_watch_txt(watch_id)
    print(files_and_types)
    if not(files_and_types):
        return caption
    if len(files_and_types)==1:
        return (files_and_types[0][0], files_and_types[0][1], caption)
    for file_and_type in files_and_types:
        if file_and_type[1]=="photo":
            file = InputMediaPhoto(media=file_and_type[0], caption=caption)
        if file_and_type[1]=="video":
            file = InputMediaVideo(media=file_and_type[0], caption=caption)
        if file_and_type[1]=="document":
            file = InputMediaDocument(media=file_and_type[0], caption=caption)
        if file_and_type[1]=="audio":
            file = InputMediaAudio(media=file_and_type[0], caption=caption)
        files.append(file)
        caption = None
    return files

async def send_media(chat: str, bot: Bot, data: tuple, kb=None):
    media = data[0]
    media_type = data[1]
    caption = data[2]
    if media_type=="photo":
        msg = await bot.send_photo(chat_id=chat, photo=media, caption=caption, reply_markup=kb)
    if media_type=="video":
       msg = await bot.send_video(chat_id=chat, photo=media, caption=caption, reply_markup=kb)
    if media_type=="document":
       msg = await bot.send_document(chat_id=chat, photo=media, caption=caption, reply_markup=kb)
    if media_type=="audio":
       msg = await bot.send_audio(chat_id=chat, photo=media, caption=caption, reply_markup=kb)
    return msg



async def check_post(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    watch_id = await insert_watch_media(data)
    await state.update_data(watch_id = watch_id)
    keyboard = get_book_kb(watch_id)
    files = await get_files(watch_id)
    if type(files)==type(" "):
        await state.set_state(AdminFSM.check)
        await message.answer(files, reply_markup=keyboard)
        await message.answer("Отправить данное сообщение?", reply_markup=get_kb({"Отправить": "yes_post", "Не отправлять": "no_post"}, [2]))
        return
    if type(files)==type(tuple()):
        await state.set_state(AdminFSM.check)
        await send_media(message.from_user.id, bot=bot, data=files, kb=keyboard)
        await message.answer("Отправить данное сообщение?", reply_markup=get_kb({"Отправить": "yes_post", "Не отправлять": "no_post"}, [2]))
        return
    await bot.send_media_group(message.from_user.id, media=files)
    await state.set_state(AdminFSM.check)
    await message.answer("Оплатить через бот", reply_markup=keyboard)
    await message.answer("Отправить данное сообщение?", reply_markup=get_kb({"Отправить": "yes_post", "Не отправлять": "no_post"}, [2]))



@admin_router.message(AdminFSM.name, F.text)
async def get_name(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(name =message.text)
    await message.answer("Принято")
    await check_post(message, state, bot)

@admin_router.callback_query(AdminFSM.check, F.data=="yes_post")
async def send_post(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    data = await state.get_data()
    watch_id = data["watch_id"]
    keyboard = get_book_kb(watch_id)
    files = await get_files(watch_id)
    if type(files)==type(" "):
        msg = await bot.send_message(chat_id=CHANNEL, text=files, reply_markup=keyboard)
        await upd_channel_msg_id(data["watch_id"], msg.message_id)
        await call.message.answer("Сообщение отправлено")
        return
    if type(files)==type(tuple()):
        msg = await send_media(chat=CHANNEL, bot=bot, data=files, kb=keyboard)
        await upd_channel_msg_id(data["watch_id"], msg.message_id)
        await call.message.answer("Сообщение отправлено")
        return
    await bot.send_media_group(chat_id=CHANNEL, media=files)
    msg = await bot.send_message(chat_id=CHANNEL, text="Оплатить через бот", reply_markup=keyboard)
    await upd_channel_msg_id(data["watch_id"], msg.message_id)
    await call.message.answer("Сообщение отправлено")
    

@admin_router.callback_query(AdminFSM.check, F.data=="no_post")
async def not_send_post(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:   
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        print("не удалось удалить кнопки")
    await state.clear()
    
    await call.message.answer("Отправка отменена")

def parse_admins(admins):
    adm_str = "\n".join(admins)
    text = f''' В настоящее время админами являются:
{adm_str}'''
    return text

@admin_router.message(AdminFSM.ADD, F.text)
async def add_admin_handler(message: types.Message, state: FSMContext):
    username = message.text
    user_exists = await exist_user_by_username(username)
    if user_exists:
        await add_admin(username)
        await message.answer("Пользователь успешно добавлен в админы")
        await state.clear()
        return
    else: 
        await message.answer("Такого пользователя нет в базе данных бота. Возможно он сменил username")

@admin_router.message(AdminFSM.REMOVE, F.text)
async def remove_admin_handler(message: types.Message, state: FSMContext):
    username = message.text
    user_exists = await exist_user_by_username(username)
    if user_exists:
        if str(ADMIN)==(await get_user_by_username(username)):
            await message.answer("Вы не можете удалить главного администратора")
            await state.clear()
            return
        await delete_admin(username)
        await message.answer("Пользователь успешно удален из списка админов")
        await state.clear()
        return
    else: 
        await message.answer("Такого пользователя нет в базе данных бота. Возможно он сменил username")
   
