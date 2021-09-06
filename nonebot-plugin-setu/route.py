"""
 - Author: DiheChen
 - Date: 2021-08-31 20:04:17
 - LastEditTime: 2021-09-06 21:40:29
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import path

from fastapi.responses import FileResponse, Response
from nonebot import get_asgi

from .util import fetch_image

app = get_asgi()

image_cache_path = path.abspath(path.join(path.dirname(__file__), "image"))


@app.get("/pixiv/{pixiv_image_url:path}")
async def _(pixiv_image_url: str):
    if path.exists(cache := path.join(image_cache_path, pixiv_image_url.split("/")[-1])):
        return FileResponse(cache)
    if (res := await fetch_image(pixiv_image_url)) is None:
        return
    image, content_type = res
    headers = {
        "cache-control": "no-cache",
        "Content-Type": content_type
    }
    return Response(image, headers=headers, media_type="stream")
