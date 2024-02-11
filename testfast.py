from fastapi import FastAPI
import datetime

app = FastAPI()

@app.get("/time")
async def get_time(time: datetime.datetime):
    print(time)
    with open("test5.txt", "a") as f:
        f.write(time.isoformat())
