"""
 - Author: DiheChen
 - Date: 2021-08-31 19:44:57
 - LastEditTime: 2021-09-06 21:40:33
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import path
from re import findall
from sys import platform
from typing import List, Optional, Tuple, Union
from urllib.parse import urljoin

from aiohttp import ClientSession, request
from nonebot.adapters.cqhttp.message import MessageSegment

from .config import config

image_cache_path = path.abspath(path.join(path.dirname(__file__), "image"))

if platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

headers = {
    "Referer": "https://www.pixiv.net",
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 "
        "Safari/537.36",
}


async def fetch_image(image_path: str) -> Optional[Tuple[bytes, str]]:
    try:
        assert image_path.startswith(("img-original", "img-master", "c/"))
        async with request("GET", "https://i.pximg.net/" + image_path, headers=headers,
                           proxy=config.proxy) as resp:
            return await resp.read(), resp.headers["Content-Type"]
    except:
        return


async def ajax_pixiv(illust_id: int) -> Optional[List[Union[str, MessageSegment]]]:
    try:
        async with ClientSession() as session:
            async with session.get(f"https://www.pixiv.net/ajax/illust/{illust_id}", headers=headers,
                                   proxy=config.proxy, verify_ssl=False) as resp:
                url: str = (data := await resp.json())["body"]["urls"]["original"]
                count = data["body"]["userIllusts"][str(
                    illust_id)]["pageCount"]
                urls = [url.replace("_p0", f"_p{i}") for i in range(count)]
                if config.url_only:
                    return [urljoin(config.public_address,
                                    "pixiv/") + "/".join(url.split("/")[3:]) for url in urls]
                if config.online_mode_pure:
                    return [MessageSegment.image(urljoin(config.public_address,
                                                         "pixiv/") + "/".join(url.split("/")[3:])) for url in urls]
                for url in urls:
                    if not path.exists(image_path := path.join(image_cache_path, url.split("/")[-1])):
                        with open(image_path, "wb") as file:
                            async with session.get(url, headers=headers, proxy=config.proxy) as res:
                                file.write(await res.read())
                return [MessageSegment.image("file:///" + path.join(image_cache_path,
                                                                    url.split("/")[-1])) for url in urls]
    except:
        return


def get_user_qq(raw_message: str) -> List[int]:
    raw = map(int, findall(r'\[CQ:at,qq=([1-9][0-9]{4,})\]', raw_message))
    return list(set(i for i in raw))
