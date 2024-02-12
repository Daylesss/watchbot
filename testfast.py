# from fastapi import FastAPI
# import datetime

# app = FastAPI()

# @app.get("/time")
# async def get_time(time: datetime.datetime):
#     print(time)
#     with open("test5.txt", "a") as f:
#         f.write(time.isoformat())
from functools import wraps
import asyncio

def retry(times=2):
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
            return func(*args, **kwargs)
        return newfn
    return decorator

@retry(2)
async def fg(i: int =2):
    print(f"{i}")
    print(1/0)

async def main():
    await fg(3)

if __name__=="__main__":
    asyncio.run(main())