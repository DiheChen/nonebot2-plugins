"""
 - Author: DiheChen
 - Date: 2021-09-02 11:12:21
 - LastEditTime: 2021-09-16 22:16:27
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import mkdir, path
from time import localtime, strftime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from aiohttp import ClientSession
from loguru import logger
from nonebot.adapters.cqhttp.message import MessageSegment

from .config import config
from .util import headers
from .validation import RequestData

image_cache_path = path.abspath(path.join(path.dirname(__file__), "image"))


class LoliconAPI:

    def __init__(self, params: RequestData) -> None:
        self.api_url = "https://api.lolicon.app/setu/v2"
        self.params = params
        self._session = ClientSession()

    async def __aenter__(self):
        res = await self._post()
        self.error: str = res["error"]
        self.response: List[Dict] = [data for data in res["data"]]
        return self

    async def _post(self) -> Optional[Dict[str, Any]]:
        async with self._session.post(self.api_url, json=self.params.dict()) as resp:
            if resp.ok:
                return await resp.json()

    async def _get_image(self, url: str) -> Union[str, MessageSegment]:
        if config.online_mode_pure:
            return MessageSegment.image(urljoin(config.public_address,
                                                "pixiv/") + "/".join(url.split("/")[3:]))
        try:
            assert not config.url_only
            if not path.exists(image_path := path.join(image_cache_path, url.split("/")[-1])):
                async with self._session.get(url, headers=headers, proxy=config.proxy, verify_ssl=False) as resp:
                    with open(image_path, "wb") as file:
                        file.write(await resp.read())
            return MessageSegment.image("file:///" + image_path)
        except:
            return urljoin(config.public_address, "pixiv/") + "/".join(url.split("/")[3:])

    async def generate_msgs(self) -> List[str]:
        return ["\n".join([
            "标题:  {}".format(res["title"]),
            "作者:  {}".format(res["author"]),
            "高度 / 宽度:  {}, {}".format(res["height"], res["width"]),
            "插画 id:  {}".format(res["pid"]),
            "限制级作品:  {}".format("是" if res["r18"] else "否"),
            "含有以下成分: {}".format(", ".join([i for i in res["tags"]])),
            "上传时间:  {}".format(LoliconAPI.format_time(res["uploadDate"])),
            str(await self._get_image(res["urls"][self.params.size]))
        ]) for res in self.response]

    async def auto_fetch(self):
        for res in self.response:
            await self._get_image(url := res["urls"][self.params.size])
            logger.info(f"Successfully downloaded image: {url}")
        return

    @property
    def tags(self):
        result: List[str] = list()
        for data in self.response:
            result.extend(data["tags"])
        return result

    @staticmethod
    def format_time(time_stamp: int) -> str:
        return strftime("%Y-%m-%d %H:%M:%S", localtime(time_stamp / 1000))

    async def __aexit__(self, *args):
        await self._session.close()
