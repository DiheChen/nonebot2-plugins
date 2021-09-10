"""
 - Author: DiheChen
 - Date: 2021-08-31 19:45:30
 - LastEditTime: 2021-09-10 19:17:18
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from asyncio import sleep
from collections import Counter
from os import mkdir, path
from random import choice, random
from typing import Dict, Iterable

from loguru import logger
from nonebot import get_driver, require
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import (Event, GroupMessageEvent,
                                           MessageEvent, PrivateMessageEvent)
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from nonebot.exception import ActionFailed, FinishedException, IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.plugin import MatcherGroup
from nonebot.typing import T_State

from . import route
from .config import config
from .data import Block, UserXP
from .lolicon_api import LoliconAPI
from .util import ajax_pixiv, get_user_qq
from .validation import RequestData

scheduler = require("nonebot_plugin_apscheduler").scheduler

num_dict = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

global_config = get_driver().config

image_cache_path = path.abspath(path.join(path.dirname(__file__), "image"))
if not path.exists(image_cache_path):
    mkdir(image_cache_path)


async def send_forward_msg(msgs: Iterable, bot: Bot, event: Event):
    if isinstance(msgs, (str, Message, MessageSegment)):
        msgs = (msgs,)
    if isinstance(event, PrivateMessageEvent):
        await send_msgs(msgs, bot, event)
    elif isinstance(event, GroupMessageEvent):
        msgs = [{
            "type": "node",
            "data": {
                "name": choice(list(global_config.nickname)),
                "uin": str(event.self_id),
                "content": Message(msg)
            }
        } for msg in msgs]
        try:
            msg_id = (await bot.send_group_forward_msg(group_id=event.group_id, messages=msgs))["message_id"]
        except ActionFailed as e:
            logger.exception(
                f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}')
            return
    else:
        return
    if config.recall_time:
        await sleep(config.recall_time)
        await bot.delete_msg(message_id=msg_id)
    raise FinishedException


async def send_msgs(msgs: Iterable, bot: Bot, event: Event):
    if isinstance(msgs, (str, Message, MessageSegment)):
        msgs = (msgs,)
    msg_ids = list()
    for msg in msgs:
        try:
            msg_ids.append((await bot.send(event, Message(msg)))["message_id"])
        except ActionFailed as e:
            logger.exception(
                f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}')
    if config.recall_time:
        await sleep(config.recall_time)
        for msg_id in msg_ids:
            await bot.delete_msg(message_id=msg_id)
    raise FinishedException


async def auto_fetch_setu():
    params = {
        "num": config.auto_fetch if config.auto_fetch <= 100 else 100
    }
    rd = RequestData(**params)
    async with LoliconAPI(params=rd) as api:
        await api.auto_fetch()
    return


if not config.url_only and not config.online_mode_pure and config.auto_fetch:
    scheduler.add_job(auto_fetch_setu, "interval", minutes=30)

matchers = MatcherGroup()
call_setu = matchers.on_regex(
    r"^[来给发]?([0-9]{1,2}|[一二三四五六七八九十])?([点份张])?([Rr]18的?)?(.{1,20})?[涩|色]图$",
    priority=5, block=True
)


@call_setu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        params = dict()
        num, _, is_r18, keyword = state["_matched_groups"]
        if num:
            num = int(num if num.isdigit() else num_dict[num])
            params.update(
                {"num": config.single_image_limit if num > config.single_image_limit else num})
        if is_r18:
            if config.global_r18:
                params.update({"r18": 1})
        if keyword:
            params.update({"keyword": keyword})
        else:
            if config.personalized_recommendation and (random() > 0.5):
                if res := list(UserXP.select().where(UserXP.user_id == event.user_id, UserXP.count > 500)):
                    params.update({"tag": [[choice(res).tag]]})
        if config.reverse_proxy:
            params.update({"proxy": config.reverse_proxy})
        rd = RequestData(**params)
        async with LoliconAPI(params=rd) as api:
            statistics = dict(sorted(Counter(tags := api.tags).items(), key=lambda x: x[1],
                                     reverse=True)[:len(tags) if len(tags) < 10 else 10])
            for tag, count in statistics.items():
                if tag not in config.useless_tag and not tag.endswith("users入り"):
                    if res := UserXP.get_or_none(user_id=event.user_id, tag=tag):
                        UserXP.replace_many(
                            [{"user_id": event.user_id, "tag": tag,
                              "count": res.count + count}]).execute()
                    else:
                        UserXP.replace_many(
                            [{"user_id": event.user_id, "tag": tag, "count": count}]).execute()
            if msgs := await api.generate_msgs():
                if config.use_forward:
                    await send_forward_msg(msgs, bot, event)
                else:
                    await send_msgs(msgs, bot, event)
    else:
        logger.warning("Not supported: setu.")
        return


get_pixiv_image = matchers.on_command(
    "/pixiv", aliases={"/pid"}, priority=1, block=True
)


@get_pixiv_image.handle()
async def _(bot: Bot, event: Event):
    if isinstance(event, MessageEvent):
        if (illust_id := event.get_plaintext()).isdigit() and (msgs := await ajax_pixiv(int(illust_id))):
            if config.use_forward:
                await send_forward_msg(msgs, bot, event)
            else:
                await send_msgs(msgs, bot, event)
        else:
            try:
                await get_pixiv_image.finish("Invalid input.")
            except ActionFailed as e:
                logger.exception(
                    f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}')
                return
    else:
        logger.warning("Not supported: setu.")
        return


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        if matcher.plugin_name == "nonebot-plugin-setu":
            if "启用" in event.raw_message or "开启" in event.raw_message:
                return
            if isinstance(event, PrivateMessageEvent):
                if Block.get_or_none(user_id=event.user_id):
                    raise IgnoredException("This user is blocked.")
            if isinstance(event, GroupMessageEvent):
                if Block.get_or_none(group_id=event.group_id) or Block.get_or_none(user_id=event.user_id):
                    raise IgnoredException("This group is blocked.")
    else:
        logger.warning("Not supported: setu.")
        return


set_group_block = matchers.on_command(
    "禁用色图", aliases={"关闭色图"}, permission=SUPERUSER, priority=5, block=True)
cancel_group_block = matchers.on_command(
    "启用色图", aliases={"开启色图"}, permission=SUPERUSER, priority=5, block=True)


@set_group_block.handle()
async def _(bot: Bot, event: Event):
    if isinstance(event, GroupMessageEvent):
        Block.replace(group_id=event.group_id).execute()
        await set_group_block.finish("\n".join([
            f"> {event.sender.card or event.sender.nickname}",
            "h 是不行的!"
        ]))
    elif isinstance(event, PrivateMessageEvent):
        if group_ids := list(map(int, filter(lambda x: x.isdigit(), event.get_plaintext().split()))):
            Block.replace_many([
                {"group_id": group_id} for group_id in group_ids
            ]).execute()
            await set_group_block.finish("\n".join([
                f"> {event.sender.card or event.sender.nickname}",
                "h 是可以的: " + ", ".join(list(map(str, group_ids)))
            ]))
    else:
        logger.warning("Not supported: setu.")
        return


@cancel_group_block.handle()
async def _(bot: Bot, event: Event):
    if isinstance(event, GroupMessageEvent):
        Block.delete().where(Block.group_id == event.group_id).execute()
        await cancel_group_block.finish("\n".join([
            f"> {event.sender.card or event.sender.nickname}",
            "h 是可以的!"
        ]))
    elif isinstance(event, PrivateMessageEvent):
        if group_ids := list(map(int, filter(lambda x: x.isdigit(), event.get_plaintext().split()))):
            result = [group_id for group_id in group_ids if Block.delete().where(
                Block.user_id == group_id).execute()]
            await set_group_block.finish("\n".join([
                f"> {event.sender.card or event.sender.nickname}",
                "h 是不行的: " + ", ".join(list(map(str, result)))
            ]))
    else:
        logger.warning("Not supported: setu.")
        return


set_user_block = matchers.on_command(
    "拉黑用户", permission=SUPERUSER, priority=5, block=True
)
cancel_user_block = matchers.on_command(
    "解封用户", permission=SUPERUSER, priority=5, block=True
)


@set_user_block.handle()
async def _(bot: Bot, event: Event):
    user_ids = None
    if isinstance(event, GroupMessageEvent):
        user_ids = get_user_qq(event.raw_message)
    elif isinstance(event, PrivateMessageEvent):
        user_ids = list(
            map(int, filter(lambda x: x.isdigit(), event.get_plaintext().split())))
    if user_ids:
        Block.replace_many([{
            "user_id": user_id
        } for user_id in user_ids]).execute()
        await set_user_block.finish("\n".join([
            f"> {event.sender.card or event.sender.nickname}",
            "h 是不行的: " + ", ".join(list(map(str, user_ids)))
        ]))


@cancel_user_block.handle()
async def _(bot: Bot, event: Event):
    result = None
    if isinstance(event, GroupMessageEvent):
        if user_ids := get_user_qq(event.raw_message):
            result = [user_id for user_id in user_ids if Block.delete().where(
                Block.user_id == user_id).execute()]
    elif isinstance(event, PrivateMessageEvent):
        if user_ids := list(map(int, filter(lambda x: x.isdigit(), event.get_plaintext().split()))):
            result = [user_id for user_id in user_ids if Block.delete().where(
                Block.user_id == user_id).execute()]
    if result:
        await cancel_user_block.finish("\n".join([
            f"> {event.sender.card or event.sender.nickname}",
            "h 是可以的: " + ", ".join(list(map(str, result)))
        ]))


get_user_xp = matchers.on_command(
    "查询xp", aliases={"查询XP"}, priority=1, block=True
)
get_group_xp = matchers.on_command(
    "xp排行榜", aliases={"XP排行榜"}, priority=1, block=True
)


@get_user_xp.handle()
async def _(bot: Bot, event: Event):
    if isinstance(event, MessageEvent):
        if user_ids := get_user_qq(event.raw_message):
            pass
        else:
            user_ids = (event.user_id,)
        for user_id in user_ids:
            if res := UserXP.select().where(UserXP.user_id == user_id):
                if user_id != event.user_id and isinstance(event, GroupMessageEvent):
                    user_info = await bot.get_group_member_info(group_id=event.group_id,
                                                                user_id=user_id, no_cache=True)
                    card, nickname, name = user_info["card"], user_info[
                        "nickname"], "他" if user_info["sex"] == "male" else "她"
                else:
                    card, nickname, name = event.sender.card, event.sender.nickname, "你"
                buf: Dict[str, int] = dict([(r.tag, r.count) for r in res])
                statistics = dict(sorted(list(buf.items()), key=lambda x: x[1],
                                         reverse=True)[:len(buf) if len(buf) < 10 else 10])
                await get_user_xp.send("\n".join([
                    f"> {card or nickname}",
                    f"{name}喜欢以下元素:" + ", ".join(list(statistics.keys())[
                                                 :int(len(statistics) / 2)]),
                    f"{name}可能对以下元素感兴趣:" + ", ".join(list(statistics.keys())[
                                                     int(len(statistics) / 2):])
                ]))
            raise FinishedException
        await get_user_xp.finish(f"我也不知道ta的xp呢~")
    else:
        logger.warning("Not supported: setu.")
        return


@get_group_xp.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if (tag := event.get_plaintext()) in config.useless_tag:
        await get_group_xp.finish("这个 tag 太常见了不会被统计哦~")
    else:
        if res := UserXP.select().where(UserXP.tag == tag):
            result = [f"> {event.sender.card or event.sender.nickname}"]
            group_member_list = await bot.get_group_member_list(group_id=event.group_id)
            user_ids = [member["user_id"] for member in group_member_list]
            buf: Dict[int, int] = dict(
                [(r.user_id, r.count) for r in res if r.user_id in user_ids])
            statistics = dict(sorted(buf.items(), key=lambda x: x[1],
                                     reverse=True)[:len(buf) if len(buf) < 10 else 10])
            count_ = 1
            for user, count in statistics.items():
                user_info = [
                    member for member in group_member_list if member["user_id"] == user][0]
                card, nickname, name = user_info["card"], user_info[
                    "nickname"], "他" if user_info["sex"] == "male" else "她"
                result.append("\n".join([
                    f"第 {count_} 喜欢 {tag} 的人是 {card or nickname} ({user}) ~",
                    f"{name} 已经看了 {count} 张含有 {tag} 的涩图啦 ~"
                ]))
                count_ += 1
            try:
                await get_group_xp.finish("\n".join(result))
            except ActionFailed as e:
                logger.exception(
                    f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}')
                return
        else:
            await get_group_xp.finish("\n".join([
                f"> {event.sender.card or event.sender.nickname}",
                "这个xp太怪了, 没有人喜欢 ~"
            ]))
