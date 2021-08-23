"""
 - Author: DiheChen
 - Date: 2021-08-23 15:06:44
 - LastEditTime: 2021-08-23 16:50:07
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from loguru import logger
from nonebot.plugin import on_regex
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, MessageEvent
from nonebot.typing import T_State
from nonebot.exception import ActionFailed

from .data import DescribeInstances
from .fetch import fetch_data, processing_data

nlp = on_regex(r'^(你?知道)?(.{1,32}?)是(什么|谁|啥)吗?[?？]?$', priority=5, block=False)


@nlp.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        instances = state["_matched_groups"][1]
        result = DescribeInstances.get_or_none(instances=instances)
        if result:
            msg = str(result.describe).replace("|@|", "\n|@|")
        else:
            msg = processing_data(await fetch_data(instances=instances)).replace("|@|", "\n|@|")
        try:
            await nlp.finish("\n".join([f"> {event.sender.card or event.sender.nickname}",
                                        msg]))
        except ActionFailed as e:
            logger.exception(
                f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
            )
            return
    else:
        logger.warning("Not supported: DescribeInstances.")
        return
