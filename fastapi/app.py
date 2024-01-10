from fastapi import FastAPI
# from pydantic import BaseModel
from database import watch_status_done, create_transaction
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
    await watch_status_done(tg_id)

    await create_transaction(tg_id=tg_id, data=data)

