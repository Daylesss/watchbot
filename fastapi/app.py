from fastapi import FastAPI
# from pydantic import BaseModel
from database import get_watch_id, watch_status_done

app = FastAPI()

@app.post("/webhook/{tg_id}")
async def get_webhook(tg_id: int, payment: dict):
    await watch_status_done(tg_id)
    print(payment)
    with open("payments.txt", "a", encoding= "utf-8") as f:
        f.write(str(payment))
    return

@app.get("/get_payment/{tg_id}")
async def check_payment(tg_id: int):
    w_id =await get_watch_id(tg_id)
    res = "!!!!!!!!!!!!"+str(w_id)+"!!!!!!!!!!!!!!!!"
    return res