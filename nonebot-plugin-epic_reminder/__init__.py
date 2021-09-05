"""
 - Author: DiheChen
 - Date: 2021-08-27 08:55:35
 - LastEditTime: 2021-08-30 11:01:29
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from time import time

from loguru import logger
from nonebot import require, get_driver
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER
from nonebot.plugin import MatcherGroup
from nonebot.typing import T_State

from .draw_image import GenerateImage
from .util import date2time_stamp, fetch_data, get_data, startup_hook

driver = get_driver()
scheduler = require("nonebot_plugin_apscheduler").scheduler
driver.on_startup(startup_hook)
scheduler.add_job(fetch_data, "cron", day_of_week="thu", hour=23, minute=1)

matchers = MatcherGroup()
query_free_game = matchers.on_regex(
    r"^(epic)?(.{2})?免费游戏$", priority=5, block=True)
force_update = matchers.on_command(
    "epic数据更新", permission=SUPERUSER, priority=1, block=True)


@query_free_game.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        if state["_matched_groups"][1] in ["本期", "本周"]:
            data = [i for i in get_data() if time() >
                    date2time_stamp(i["start_date"])]
        elif state["_matched_groups"][1] in ["下期", "下周"]:
            data = [i for i in get_data() if time() <
                    date2time_stamp(i["start_date"])]
        else:
            data = get_data()
        async with GenerateImage(data) as gi:
            reply = MessageSegment.image(await gi.generate_image())
            await query_free_game.finish(MessageSegment.reply(event.message_id) + reply)
    else:
        logger.warning("Not supported: epic reminder.")
        return


@force_update.handle()
async def _(bot: Bot, event: Event):
    if isinstance(event, MessageEvent):
        await fetch_data()
        try:
            await force_update.finish("\n".join([
                f"> {event.sender.card or event.sender.nickname}",
                "已执行更新。"
            ]))
        except ActionFailed as e:
            logger.exception(
                f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
            )
            return
    else:
        logger.warning("Not supported: epic reminder.")
        return
