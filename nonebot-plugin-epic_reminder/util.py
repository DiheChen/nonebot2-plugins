"""
 - Author: DiheChen
 - Date: 2021-08-27 08:56:04
 - LastEditTime: 2021-08-28 21:05:22
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import path
from time import mktime, strptime
from typing import List, Optional

from aiohttp import ClientSession
from loguru import logger

try:
    import ujson as json
except ImportError:
    import json

epic_free_game_data = None
cache_data = path.abspath(path.join(path.dirname(__file__), "cache.json"))


async def startup_hook():
    if not path.exists(path.abspath(path.join(path.dirname(__file__), "cache.json"))):
        await fetch_data()
    with open(cache_data, "r") as f:
        global epic_free_game_data
        epic_free_game_data = json.loads(f.read())
    return None


def date2time_stamp(date: str):
    return mktime(strptime(date.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S.000"))


async def fetch_data() -> Optional[str]:
    params = {
        "locale": "zh-CN",
        "country": "CN",
        "allowCountries": "CN"
    }
    try:
        async with ClientSession() as session:
            async with session.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions",
                                   params=params) as resp:
                with open(cache_data, "w") as file:
                    global epic_free_game_data
                    file.write(json.dumps(epic_free_game_data := await resp.json(), indent=4))
                    return None
    except Exception as e:
        logger.exception(e)
        return str(e)


def get_data() -> Optional[List]:
    if epic_free_game_data:
        free_games = [i for i in epic_free_game_data["data"]["Catalog"]
                      ["searchStore"]["elements"] if i["promotions"]]
        data = [{
            "title": free_game["title"],
            "description": free_game["description"],
            "url": free_game["keyImages"][0]["url"],
            "original_price": free_game["price"]["totalPrice"]["fmtPrice"]["originalPrice"],
            "start_date": (free_game["promotions"]["promotionalOffers"] or free_game["promotions"][
                "upcomingPromotionalOffers"])[0]["promotionalOffers"][0]["startDate"],
            "end_date": (free_game["promotions"]["promotionalOffers"] or free_game["promotions"][
                "upcomingPromotionalOffers"])[0]["promotionalOffers"][0]["endDate"]
            } for free_game in free_games]
        return data
