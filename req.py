import requests
import hashlib
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageFont
def make_hash(data: dict):
    hash_dict2 = {
    "payerAddress": data["address"],
    "amount": data["price"],
    "network": data["network"],
    "webhookUrl": "https://webhook-test.com/088182844c158e86e1636156dbabd546",
    "payment_type": "investment",
    }
    hash_list = list(hash_dict2.keys())
    hash_list = sorted(hash_list)
    hash_str = "".join(str(hash_dict2[i]) for i in hash_list)+"secret"

    hash = hashlib.md5(hash_str.encode()).hexdigest()
    return {
    "payerAddress": data["address"],
    "amount": data["price"],
    "network": data["network"],
    "webhookUrl": "https://webhook-test.com/088182844c158e86e1636156dbabd546",
    "payment_type": "investment",
    "hash": hash
    }

data = {"address": "0x0261036567Bf14666C67a35C2A204eb302E11D85",
        "price": 1,
    "network": "erc20"}

async def main():
    async with aiohttp.ClientSession() as session:
        res = await session.post("https://webhook-test.com/088182844c158e86e1636156dbabd546", json= make_hash(data))
        print(res)
    #     res = await res.json()
    #     print(res)
    # qrcd = res.get("qrCode")
    # font_path = r"DejaVuSansMono.ttf"  
    # font_size = 24
    # font = ImageFont.truetype(font_path, font_size)
    # img = Image.new('RGB', (580, 550), color=(255,255,255))
    # d = ImageDraw.Draw(img)
    # d.text((0, 0), qrcd, font=font, fill=(0, 0, 0))
    # qr_name = f"test.png"
    # img.save(qr_name)

if __name__=="__main__":
    asyncio.run(main())
# res = requests.post("http://78.40.216.26:3001/payment", json= make_hash(data))
# print(res.status_code)