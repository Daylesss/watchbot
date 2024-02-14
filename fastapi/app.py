import logging
from fastapi import FastAPI
import asyncio
import hashlib
from database import set_watch_status, create_transaction
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(filename = "logs/py_log.log")]
)

def check_hash(data: dict):
    hash = data.pop("hash")
    hash_list = list(data.keys())
    hash_list = sorted(hash_list)
    hash_str = "".join(str(data[i]) for i in hash_list)+ "secret"
    hash_to_check = hashlib.md5(hash_str.encode()).hexdigest()
    if hash == hash_to_check:
        return True

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://78.40.216.26:3001"],
    allow_methods=['*'],
    allow_headers=["*"]
)

@app.post("/webhook/{tg_id}")
async def get_webhook(tg_id: int, data: dict):
    logging.info(f"Webhook received {data}")
    if not check_hash(data):
        logging.error("WRONG HASH %s", data)
    if int(data["orderAmount"])==int(data["totalRecieved"]):
        for i in range(5):
            try:
                is_ok = await set_watch_status(tg_id, "Done")
            except Exception as er:
                logging.error(er, exc_info=True)
                continue
            if is_ok:
                break
            else:
                asyncio.sleep(0.5)
    elif int(data["orderAmount"])<int(data["totalRecieved"]):
        for i in range(5):
            try:
                is_ok = await set_watch_status(tg_id, "lower_price")
            except Exception as er:
                logging.error(er, exc_info=True)
                continue
            if is_ok:
                break
            else:
                asyncio.sleep(0.5)
    else: 
        for i in range(5):
            try:
                is_ok = await set_watch_status(tg_id, "higher_price")
            except Exception as er:
                logging.error(er, exc_info=True)
                continue
            if is_ok:
                break
            else:
                asyncio.sleep(0.5)
    logging.info(f"Creating transaction tg_id = {tg_id} {data}")
    await create_transaction(tg_id=tg_id, data=data)

