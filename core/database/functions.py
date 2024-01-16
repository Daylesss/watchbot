import json
from sqlalchemy import select, insert, update, desc
from core.database.database import async_session_maker
from core.database.models import user, order, watch, transaction, watch_file
from sqlalchemy.exc import OperationalError


async def new_user_db(tg_id: int, username:str):
    async with async_session_maker() as session:
        query = select(user).where(user.c.tg_id==tg_id)
        query= await session.execute(query)
        if not (query.first()):
            stmt = insert(user).values(tg_id=tg_id, username=username)
            await session.execute(stmt)
            await session.commit()
            return True
        else: return False

async def get_user_by_username(username:str):
    async with async_session_maker() as session:
        query = select(user).where(user.c.username==username)
        res = await session.execute(query)
        return bool(res.first())

async def get_user_watch_status_db(tg_id: int):
    async with async_session_maker() as session:
        j = user.join(order, user.c.order_id==order.c.order_id, isouter=True)\
            .join(watch, watch.c.watch_id==order.c.watch_id, isouter=True)
        query = select(watch.c.status).select_from(j).where(user.c.tg_id==tg_id)
        res = await session.execute(query)
        res = res.first()
        if not(res[0]):
            return "no_order"
        
        return res[0]


async def get_channel_message(tg_id: int):
    async with async_session_maker() as session:
        j = user.join(order, user.c.order_id==order.c.order_id).join(watch, order.c.watch_id==watch.c.watch_id)
        query = select(watch.c.channel_message_id).select_from(j)
        res = await session.execute(query)
        res = res.first()
        return res[0]

async def insert_watch_db(data: dict):
    async with async_session_maker() as session:
        stmt = insert(watch).values(watch_name=data["name"], admin_message_id=data["message_id"], price = int(data["price"]), booking_price = int(data["price2"]))\
            .returning(watch.c.watch_id)
        watch_id = await session.execute(stmt)
        watch_id = watch_id.first()
        await session.commit()
        return watch_id[0]

async def insert_watch_media(data: dict):
    async with async_session_maker() as session:
        stmt = insert(watch).values(watch_name=data["name"], unique_file_id=data["unique_id"], msg_txt = data["message_text"],
                                    price = int(data["price"]), booking_price = int(data["price2"]))\
            .returning(watch.c.watch_id)
        watch_id = await session.execute(stmt)
        watch_id = watch_id.first()
        await session.commit()
        return watch_id[0]

# async def get_watch_files(watch_id: int):
#         async with async_session_maker() as session:
#             query = select(watch.c.files).where(watch.c.watch_id==watch_id)
#             res = await session.execute(query)
#             return json.loads(res.first()[0])

async def get_watch_txt(watch_id: int):
        async with async_session_maker() as session:
            query = select(watch.c.msg_txt).where(watch.c.watch_id==watch_id)
            res = await session.execute(query)
            return res.first()[0]

    
async def upd_channel_msg_id(watch_id: int, msg_id: int):
    async with async_session_maker() as session:
        query = select(watch.c.channel_message_id).where(watch.c.watch_id==watch_id)
        res = await session.execute(query)
        res = res.first()
        if not(res[0]):
            stmt = update(watch).where(watch.c.watch_id==watch_id).values(channel_message_id=msg_id)
            await session.execute(stmt)
            await session.commit()

async def new_order_db(tg_id: int, watch_id: int):
    async with async_session_maker() as session:
        stmt = insert(order).values(tg_id=tg_id, watch_id=watch_id).returning(order.c.order_id)
        order_id = await session.execute(stmt)
        order_id = order_id.first()[0]
        stmt = update(user).where(user.c.tg_id==tg_id).values(order_id=order_id)
        await session.execute(stmt)
        
        await session.commit()

async def set_pay_params_db(tg_id: int, data:dict):
    async with async_session_maker() as session:
        j = user.join(order, user.c.order_id == order.c.order_id).join(watch, order.c.watch_id == watch.c.watch_id)
        query = select(watch.c.price, user.c.order_id, watch.c.booking_price).select_from(j).where(user.c.tg_id == tg_id)
        res = await session.execute(query)
        res = res.first()
        price = res[0]
        order_id = res[1]
        if data["book_or_buy"]=="book":
            price = res[2]
        
        stmt = update(order).where(order.c.order_id==order_id)\
            .values(book_or_buy=data["book_or_buy"], order_price=price, network=data["network"], address=data["address"])
        await session.execute(stmt)
        await session.commit()
    return price


async def upd_watch_book_status_db(tg_id: int, watch_id: int, old_status:str = "for_sale", new_status: str= "booking", order_none: bool=False):
    async with async_session_maker() as session:
        try:
            if not(order_none):
                query = select(user.c.order_id).where(user.c.tg_id==tg_id)
                res = await session.execute(query)
                order_id = res.first()[0]
            else: order_id = None
            query = select(watch.c.status).where(watch.c.watch_id==watch_id).with_for_update()
            res = (await session.execute(query)).first()
            if res[0]==old_status:
                stmt = update(watch).where(watch.c.watch_id==watch_id).values(status=new_status, order_id = order_id)
                await session.execute(stmt)
                await session.commit()
                return True
            else:
                return False
        except OperationalError:
            return False

async def get_adm_msg_db(watch_id: int):
    async  with async_session_maker() as session:
        query = select(watch.c.admin_message_id).where(watch.c.watch_id==watch_id)
        res = await session.execute(query)
        return res.first()

async def get_watch_id(tg_id: int):
    async  with async_session_maker() as session:
        j = user.join(order, user.c.order_id == order.c.order_id).join(watch, order.c.watch_id == watch.c.watch_id)
        query = select(watch.c.watch_id).select_from(j).where(user.c.tg_id==tg_id)
        res = await session.execute(query)
        res = res.first()
        return res[0]

async def get_ch_msg_db(watch_id: int):
    async with async_session_maker() as session:
        query = select(watch.c.channel_message_id).where(watch.c.watch_id==watch_id)
        res = await session.execute(query)
        return res.first()[0]

async def get_watch_status(watch_id: int):
    async with async_session_maker() as session:
        query = select(watch.c.status).where(watch.c.watch_id==watch_id)
        res = await session.execute(query)
        return res.first()[0]

async def get_user_order(watch_id: int):
    async with async_session_maker() as session:
        j = watch.join(order, watch.c.order_id == order.c.order_id)
        query = select(order.c.book_or_buy, order.c.order_price, watch.c.channel_message_id).select_from(j).where(watch.c.watch_id==watch_id)
        res = await session.execute(query)
        return res.first()

async def create_transaction(tg_id: int, data: dict):
    async with async_session_maker() as session:
        j = user.join(order, user.c.order_id == order.c.order_id).join(watch, order.c.watch_id == watch.c.watch_id)
        query = select(watch.c.watch_id).select_from(j).where(user.c.tg_id==tg_id)
        watch_id = (await session.execute(query)).first()[0]
        stmt = insert(transaction).values(watch_id=watch_id, transaction_data=json.dumps(data))
        await session.execute(stmt)
        await session.commit()

async def add_admin(username: str):
    async with async_session_maker() as session:
        stmt = update(user).where(user.c.username==username).values(is_admin=True)
        await session.execute(stmt)
        await session.commit()

async def delete_admin(username: str):
    async with async_session_maker() as session:
        stmt = update(user).where(user.c.username==username).values(is_admin=False)
        await session.execute(stmt)
        await session.commit()


async def get_admins_id():
    async with async_session_maker() as session:
        query = select(user.c.tg_id).where(user.c.is_admin==True)
        res = await session.execute(query)
        
        return res.scalars().all()


async def get_admins_username():
    async with async_session_maker() as session:
        query = select(user.c.username).where(user.c.is_admin==True)
        res = await session.execute(query)
        
        return res.scalars().all()

async def add_admin_by_id(tg_id: int):
    async with async_session_maker() as session:
        stmt = insert(user).values(tg_id=tg_id, username="MAIN_ADMIN", is_admin=True)
        await session.execute(stmt)
        await session.commit()


async def insert_watch_file(unique_id: str, file_id, file_type):
    async with async_session_maker() as session:
        stmt = insert(watch_file).values(unique_file_id = unique_id, file_id = file_id, file_type = file_type)
        await session.execute(stmt)
        await session.commit()

# async def insert_watch_file(unique_id: str, file_id, file_type):
#     async with async_session_maker() as session:
#         try:
#             query = select(watch.c.unique).where(watch.c.watch_id==watch_id).with_for_update()
#             res = (await session.execute(query)).first()
#             if res[0]==old_status:
#                 stmt = update(watch).where(watch.c.watch_id==watch_id).values(status=new_status, order_id = order_id)
#                 await session.execute(stmt)
#                 await session.commit()
#                 return True
#             else:
#                 return False
#         except OperationalError:
#             return False

async def get_watch_files_watch(watch_id):
    async with async_session_maker() as session:
        j = watch_file.join(watch, watch_file.c.unique_file_id==watch.c.unique_file_id, isouter=True)
        query = select(watch_file.c.file_id, watch_file.c.file_type, watch_file.c.watch_file_registred_at)\
            .select_from(j).where(watch.c.watch_id==watch_id).order_by(watch_file.c.watch_file_registred_at)
        res = await session.execute(query)

        return res.all()

async def get_watch_files_unique(unique_id:str):
    async with async_session_maker() as session:
        query = select(watch_file.c.file_id, watch_file.c.file_type, watch_file.c.watch_file_registred_at)\
            .where(watch_file.c.unique_file_id==unique_id).order_by(watch_file.c.watch_file_registred_at)
        res = await session.execute(query)

        return res.all()

async def get_transaction_data(tg_id: int):
    async with async_session_maker() as session:
        query = select(transaction.c.transaction_data).where(transaction.c.tg_id==tg_id).order_by(desc(transaction.c.transaction_time))
        res = await session.execute(query)
        return res.first()[0]
