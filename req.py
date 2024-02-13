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

def check_hash(data: dict):
    hash = data.pop("hash")
    hash_list = list(data.keys())
    hash_list = sorted(hash_list)
    hash_str = "".join(str(data[i]) for i in hash_list)+ "secret"
    hash_to_check = hashlib.md5(hash_str.encode()).hexdigest()
    if hash == hash_to_check:
        return True

data_test = {
  "payerAddress": "0x0261036567Bf14666C67a35C2A204eb302E11D85",
  "amount": 1,
  "network": "erc20",
  "webhookUrl": "https://webhook-test.com/088182844c158e86e1636156dbabd546",
  "payment_type": "investment",
  "hash": "92f6a266e293038ed5d4ea76f316778c"
}
print(check_hash(data_test))

# data = {"address": "0xA38B14B60971f6B01643C0aCDc54EcDDfF2E91Cd",
#         "price": 1,
#     "network": "erc20"}

# async def main():
#     async with aiohttp.ClientSession() as session:
#         res = await session.post("http://78.40.216.26:3001/payment", json= make_hash(data))
#         # print(res)
#         res = await res.json()
#         print(res)
#     qrcd = res.get("qrCode")
#     font_path = r"DejaVuSansMono.ttf"  
#     font_size = 24
#     font = ImageFont.truetype(font_path, font_size)
#     img = Image.new('RGB', (580, 550), color=(255,255,255))
#     d = ImageDraw.Draw(img)
#     d.text((0, 0), qrcd, font=font, fill=(0, 0, 0))
#     qr_name = f"test.png"
#     img.save(qr_name)

# if __name__=="__main__":
#     asyncio.run(main())
# # res = requests.post("http://78.40.216.26:3001/payment", json= make_hash(data))
# # print(res.status_code)