import json
import asyncio
from functools import wraps
from typing import AsyncGenerator
from datetime import datetime
from sqlalchemy import Table, Column, Integer, BigInteger, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData, Double
from sqlalchemy import MetaData, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError


from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

metadata = MetaData()

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def retry(times=2, sleep_for: int = 3):
    def decorator(func):
        @wraps(func)
        async def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    print("IT WORKS!!", flush = True)
                    return await func(*args, **kwargs)
                except Exception as err:
                    print(err, flush=True)
                    attempt += 1
                    asyncio.sleep(sleep_for)
            return func(*args, **kwargs)
        return newfn
    return decorator
        

watch = Table(
    "watch",
    metadata,
    Column("watch_id", BigInteger, primary_key=True),
    Column("channel_message_id", BigInteger),
    Column("admin_message_id", BigInteger),
    Column("unique_file_id", String, unique= True),
    Column("msg_txt", String),
    Column("price", Integer, nullable=False),
    Column("booking_price", Integer, nullable=False),
    Column("watch_name", String),
    Column("order_id", BigInteger),
    Column("status", String, nullable=False, default="for_sale"),
    Column("watch_registred_at", TIMESTAMP, default=datetime.utcnow)
)

user = Table(
    "user",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("tg_id", BigInteger, nullable=False, unique=True),
    Column("username", String),
    Column("is_admin", Boolean, nullable=False, default=False),
    Column("order_id", BigInteger),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow)
)

order = Table(
    "order",
    metadata,
    Column("order_id", BigInteger, primary_key=True),
    Column("tg_id", BigInteger, ForeignKey("user.tg_id"), nullable=False),
    Column("watch_id", BigInteger, ForeignKey("watch.watch_id"), nullable=False),
    Column("book_or_buy", String),
    Column("order_price", Double),
    Column("network", String),
    Column("address", String),
    Column("order_status", String, default="waiting"),
    Column("order_registred_at", TIMESTAMP, default=datetime.utcnow),
    )

transaction = Table(
    "transaction",
    metadata,
    Column("transaction_id", BigInteger, primary_key=True),
    Column("tg_id", BigInteger, nullable=False),
    Column("watch_id", BigInteger, ForeignKey("watch.watch_id"), nullable=False),
    Column("transaction_data", JSON, nullable=False),
    Column("transaction_time", TIMESTAMP, default=datetime.utcnow)
)

watch_file = Table(
    "watch_file",
    metadata,
    Column("watch_file_id", BigInteger, primary_key=True),
    Column("unique_file_id", String, nullable=False),
    Column("file_id", String, nullable=False),
    Column("file_type", String, nullable=False),
    Column("watch_file_registred_at", TIMESTAMP, default=datetime.utcnow),
)



@retry(5, 3)
async def get_watch_id(tg_id: int):
    async  with async_session_maker() as session:
        j = user.join(order, user.c.order_id == order.c.order_id).join(watch, order.c.watch_id == watch.c.watch_id)
        query = select(watch.c.watch_id).select_from(j).where(user.c.tg_id==tg_id)
        res = await session.execute(query)
        res = res.first()
        return res[0]

@retry(5, 3)
async def set_watch_status(tg_id: int, watch_status:str):
    async with async_session_maker() as session:
        try:
            j = user.join(order, user.c.order_id == order.c.order_id)
            query =  select(order.c.order_id, order.c.watch_id).select_from(j).where(user.c.tg_id==tg_id)
            res = await session.execute(query)
            res = res.first()
            order_id = res[0]
            watch_id = res[1]
            query = select(watch.c.status, watch.c.order_id).where(watch.c.watch_id==watch_id).with_for_update()
            res = (await session.execute(query)).first()
            if res[0]=="booking" and res[1]==order_id:
                stmt = update(watch).where(watch.c.watch_id==watch_id).values(status=watch_status)
                await session.execute(stmt)
                await session.commit()
                return True
            else: 
                return False
        except OperationalError:
            return False


@retry(5, 3)
async def create_transaction(tg_id: int, data: dict):
    async with async_session_maker() as session:
        j = user.join(order, user.c.order_id == order.c.order_id).join(watch, order.c.watch_id == watch.c.watch_id)
        query = select(watch.c.watch_id).select_from(j).where(user.c.tg_id==tg_id)
        watch_id = (await session.execute(query)).first()[0]
        stmt = insert(transaction).values(watch_id=watch_id, tg_id=tg_id, transaction_data=json.dumps(data))
        await session.execute(stmt)
        await session.commit()
            
