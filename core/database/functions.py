from sqlalchemy import select, insert
from core.database.database import async_session_maker
from core.database.models import user

async def new_user_db(id: int, username:str):
    async with async_session_maker() as session:
        query = select(user).where(user.c.tg_id==id)
        query= await session.execute(query)
        if not (query.first()):
            stmt = insert(user).values(tg_id=id, username=username)
            await session.execute(stmt)
            query = select(user)
            res = await session.execute(query)
            await session.commit()
            return True
        else: return False


# async def is

