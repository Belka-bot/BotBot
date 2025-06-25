
import aiohttp
import os

YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")
YANDEX_DISK_UPLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"

async def upload_to_yandex_disk(file_path):
    filename = os.path.basename(file_path)
    headers = {
        "Authorization": f"OAuth {YANDEX_TOKEN}"
    }
    params = {
        "path": f"/BelkaBot/{filename}",
        "overwrite": "true"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(YANDEX_DISK_UPLOAD_URL, headers=headers, params=params) as res:
            href = (await res.json())["href"]
        with open(file_path, "rb") as f:
            async with session.put(href, data=f) as put_res:
                if put_res.status == 201 or put_res.status == 200:
                    return f"https://disk.yandex.ru/client/disk/BelkaBot/{filename}"
    return "Ошибка загрузки"
