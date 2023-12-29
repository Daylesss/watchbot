from fastapi import FastAPI
# from pydantic import BaseModel
from database import get_watch_id

app = FastAPI()

@app.post("/webhook")
async def get_webhook(payment: str):
    with open("payments.txt", "a", encoding= "utf-8") as f:
        f.write(payment)
    return

@app.get("/get_payment/{tg_id}")
async def check_payment(tg_id: int):
    w_id =await get_watch_id(tg_id)
    res = "!!!!!!!!!!!!"+str(w_id)+"!!!!!!!!!!!!!!!!"
    return res