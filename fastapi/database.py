from typing import AsyncGenerator
# import time
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData, Double
from sqlalchemy import MetaData, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

metadata = MetaData()

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


watch = Table(
    "watch",
    metadata,
    Column("watch_id", Integer, primary_key=True),
    Column("channel_message_id", Integer),
    Column("admin_message_id", Integer, nullable=False),
    Column("price", Integer, nullable=False),
    Column("watch_name", String),
    Column("order_id", Integer),
    Column("status", String, nullable=False, default="for_sale"),
    Column("watch_registred_at", TIMESTAMP, default=datetime.utcnow)
)

user = Table(
    "user",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("tg_id", Integer, nullable=False, unique=True),
    Column("username", String),
    Column("order_id", Integer),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow)
)

order = Table(
    "order",
    metadata,
    Column("order_id", Integer, primary_key=True),
    Column("tg_id", Integer, ForeignKey("user.tg_id"), nullable=False),
    Column("watch_id", Integer, ForeignKey("watch.watch_id"), nullable=False),
    Column("book_or_buy", String),
    Column("order_price", Double),
    Column("network", String),
    Column("address", String),
    Column("order_status", String, default="waiting"),
    Column("order_registred_at", TIMESTAMP, default=datetime.utcnow),
    )



async def get_watch_id(tg_id: int):
    async  with async_session_maker() as session:
        j = user.join(order, user.c.order_id == order.c.order_id).join(watch, order.c.watch_id == watch.c.watch_id)
        query = select(watch.c.watch_id).select_from(j).where(user.c.tg_id==tg_id)
        res = await session.execute(query)
        res = res.first()
        return res[0]

async def watch_status_done(tg_id: int):
    async with async_session_maker() as session:
        j = user.join(order, user.c.order_id == order.c.order_id)
        query =  select(order.c.order_id, order.c.watch_id).select_from(j).where(user.c.tg_id==tg_id)
        res = await session.execute(query)
        res = res.first()
        order_id = res[0]
        watch_id = res[1]
        query = select(watch.c.status, watch.c.order_id).where(watch.c.watch_id==watch_id).with_for_update()
        res = (await session.execute(query)).first()
        if res[0]=="booking" and res[1]==order_id:
            stmt = update(watch).where(watch.c.watch_id==watch_id).values(status="Done")
            await session.execute(stmt)
            await session.commit()
            return True
        else: 
            return False
            
            
        