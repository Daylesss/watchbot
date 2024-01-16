from fastapi import FastAPI
import asyncio
from database import set_watch_status, create_transaction
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://78.40.216.26:3001"],
    allow_methods=['*'],
    allow_headers=["*"]
)

@app.post("/webhook/{tg_id}")
async def get_webhook(tg_id: int, data: dict):
    
    if int(data["orderAmount"])==int(data["totalReceived"]):
        for i in range(5):
            is_ok = await set_watch_status(tg_id, "Done")
            if is_ok:
                break
            else:
                asyncio.sleep(0.5)
    elif int(data["orderAmount"])<int(data["totalReceived"]):
        for i in range(5):
            is_ok = await set_watch_status(tg_id, "lower_price")
            if is_ok:
                break
            else:
                asyncio.sleep(0.5)
    else: 
        for i in range(5):
            is_ok = await set_watch_status(tg_id, "higher_price")
            if is_ok:
                break
            else:
                asyncio.sleep(0.5)
    await create_transaction(tg_id=tg_id, data=data)

