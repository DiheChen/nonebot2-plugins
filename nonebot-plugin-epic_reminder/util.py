"""
 - Author: DiheChen
 - Date: 2021-08-27 08:56:04
 - LastEditTime: 2021-09-24 01:40:53
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import path
from time import mktime, strptime
from typing import Any, Dict, List, Optional

from aiohttp import ClientSession
from loguru import logger

try:
    import ujson as json
except ImportError:
    import json

epic_free_game_data = None
cache_data = path.abspath(path.join(path.dirname(__file__), "cache.json"))


async def startup_hook():
    if not path.exists(cache_data):
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


def get_data() -> Optional[List[Dict[str, Any]]]:
    if epic_free_game_data:
        free_games = [i for i in epic_free_game_data["data"]["Catalog"][
            "searchStore"]["elements"] if i["promotions"]]
        result = list()
        for game in free_games:
            if game["promotions"]["promotionalOffers"]:
                extra = {
                    "start_date": game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["startDate"],
                    "end_date": game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["endDate"]
                }
            else:
                extra = {
                    "start_date": game["promotions"]["upcomingPromotionalOffers"][0]["promotionalOffers"][0]["startDate"],
                    "end_date": game["promotions"]["upcomingPromotionalOffers"][0]["promotionalOffers"][0]["endDate"]
                }
            result.append(
                dict({
                    "title": game["title"],
                    "description": game["description"],
                    "url": game["keyImages"][0]["url"],
                    "original_price": game["price"]["totalPrice"]["fmtPrice"]["originalPrice"],
                }, **extra))
        return result
