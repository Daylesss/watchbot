from fastapi import FastAPI
# from pydantic import BaseModel
from database import get_watch_id, watch_status_done

app = FastAPI()

@app.post("/webhook/{tg_id}")
async def get_webhook(tg_id: int, payment: dict):
    await watch_status_done(tg_id)

    with open("payments.txt", "a", encoding= "utf-8") as f:
        f.write(str(payment))
    return
