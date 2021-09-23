"""
 - Author: DiheChen
 - Date: 2021-08-27 08:55:31
 - LastEditTime: 2021-09-24 01:40:36
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/DiheChen
"""
from base64 import b64encode
from io import BytesIO
from os import path
from time import time
from typing import List

from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont

from .util import date2time_stamp


class GenerateImage:
    def __init__(self, data: list) -> None:
        self.data = data
        self.urls = [i["url"] for i in data]
        self._session = ClientSession()
        self._font_path = path.abspath(
            path.join(path.dirname(__file__), "msyh.ttc"))

    async def _get(self, url: str, params=None) -> Image.Image:
        async with self._session.get(url, params=params, verify_ssl=False) as resp:
            return Image.open(BytesIO(await resp.read())).convert("RGBA").resize((360, 480))

    async def __aenter__(self):
        self.images: List[Image.Image] = list()
        for url in self.urls:
            self.images.append(await self._get(url=url))
        return self

    @staticmethod
    def date2str(date: str):
        return date[0:4] + "年" + date[5:7] + "月" + date[8:10] + "日"

    def image2b64(self, image: Image.Image) -> str:
        buf = BytesIO()
        image.save(buf, format='PNG')
        base64_str = b64encode(buf.getvalue()).decode()
        return "base64://" + base64_str

    def draw_text(self, image: Image.Image, text: str, font_size: int, xy=(0, 0),
                  color=(255, 255, 255, 255)) -> Image.Image:
        font = ImageFont.truetype(self._font_path, font_size)
        new_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        ImageDraw.Draw(new_image).text(
            xy, text=text, font=font, fill=color, anchor="lt")
        return Image.alpha_composite(image, new_image)

    async def generate_image(self) -> str:
        image = Image.new(
            "RGBA", (len(self.images) * 480 - abs(len(self.images)-1 * 40) if len(self.data)
                     > 1 else 460, 720),
            (18, 18, 18, 255))
        image = self.draw_text(
            image, "免费游戏", 30, (60, 30), (255, 255, 255, 255))
        banner_draw = ImageDraw.ImageDraw(
            blue_banner := Image.new("RGBA", (360, 40)))
        for count, game_cover in enumerate(self.images):
            banner_draw.rounded_rectangle((0, 0, 360, 40), 10, fill=(
                63, 72, 204) if time() > date2time_stamp(self.data[count]["start_date"]) else (0, 0, 0))
            game_cover.paste(blue_banner.crop((0, 5, 360, 40)), (0, 445))
            image.alpha_composite(game_cover, (count * 440 + 60, 80))
            image = self.draw_text(image, "当前免费" if time() > date2time_stamp(
                self.data[count]["start_date"]) else "即将推出", 20, (count * 440 + 205, 535))
            image = self.draw_text(
                image, self.data[count]["title"], 20, (count * 440 + 60, 585))
            image = self.draw_text(
                image, "原价" + " " * 9 + self.data[count]["original_price"], 20, (count * 440 + 60, 620))
            image = self.draw_text(
                image, "开始时间:  " +
                GenerateImage.date2str(self.data[count]["start_date"]),
                20, (count * 440 + 60, 655))
            image = self.draw_text(
                image, "截止时间:  " +
                GenerateImage.date2str(self.data[count]["end_date"]),
                20, (count * 440 + 60, 680))
        return self.image2b64(image)

    async def __aexit__(self, *args):
        await self._session.close()
