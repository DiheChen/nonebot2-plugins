"""
 - Author: DiheChen
 - Date: 2021-08-24 11:32:12
 - LastEditTime: 2021-08-29 16:47:14
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from collections import Counter
from time import localtime, strftime
from typing import List, Iterable

from loguru import logger
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from nonebot.exception import ActionFailed
from nonebot.plugin import MatcherGroup
from nonebot.typing import T_State

from .data import ImageMessage


async def _image_in_msg(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupMessageEvent) and (m.type == "image" for m in event.message)

matchers = MatcherGroup(type="message")
listen = matchers.on_message(rule=_image_in_msg, priority=5, block=False)
query = matchers.on_command("查火星图", aliases={"查询火星图"}, priority=1, block=True)
summary = matchers.on_command("火星排行榜", priority=1, block=True)


def format_time(time_stamp: int) -> str:
    return strftime("%Y-%m-%d %H:%M:%S", localtime(time_stamp))


def generate_forward_msg(msgs: Iterable, self_id: int) -> List:
    if isinstance(msgs, (str, Message, MessageSegment)):
        msgs = (msgs,)
    return [{
            "type": "node",
            "data": {
                "name": "老婆~",
                # ↓ 旧版 go-cqhttp 与 onebot 标准不符, 若使用其它标准 onebot 协议端请修改下面字段为 `user_id` ↓
                "uin": str(self_id),
                "content": msg
            }
        } for msg in msgs]


@listen.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if (image_list := [s.data["file"] for s in event.message if s.type == "image" and "file" in s.data]):
        for image in image_list:
            if len(data := ImageMessage.select().where(ImageMessage.group_id == event.group_id, ImageMessage.image_md5 == image)) == 5:
                first_sender = await bot.get_group_member_info(group_id=event.group_id, user_id=data[0].user_id, no_cache=True)
                try:
                    await listen.send(MessageSegment.reply(event.message_id) + "\n".join([
                        "⚠️ 这张图片可能是火星图!",
                        f"它最早由 {first_sender['card'] or first_sender['nickname']} ({first_sender['user_id']}) 在 {format_time(data[0].time_stamp)} 发送。"])
                    )
                except ActionFailed as e:
                    logger.exception(
                        f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}')
                    return
            if (result := ImageMessage.get_or_none(user_id=event.user_id, group_id=event.group_id, image_md5=image)):
                ImageMessage.replace(time_stamp=result.time_stamp, user_id=result.user_id,
                                     group_id=result.group_id, image_md5=result.image_md5,
                                     sent_count=result.sent_count+1).execute()
            else:
                ImageMessage.replace(time_stamp=event.time, user_id=event.user_id,
                                     group_id=event.group_id, image_md5=image, sent_count=1).execute()
    return


@query.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, GroupMessageEvent):
        if event.raw_message != ("查询火星图" or "查火星图"):
            state["image"] = event.message
    else:
        logger.warning("Not supported: outdated image.")
        return


@query.got("image", prompt="请发送要查询的图片~")
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, GroupMessageEvent):
        result = [f"> {event.sender.card or event.sender.nickname}"]
        if image_list := [s.data['file'] for s in event.message if s.type == 'image' and 'file' in s.data]:
            for count, img in enumerate(image_list):
                if len(data := ImageMessage.select().where(ImageMessage.group_id == event.group_id, ImageMessage.image_md5 == img)) > 5:
                    first_sender = await bot.get_group_member_info(group_id=event.group_id, user_id=data[0].user_id, no_cache=True)
                    result.append(
                        f"第 {count + 1} 张图片是火星图, 它最早由 {first_sender['card'] or first_sender['nickname']} ({first_sender['user_id']}) 在 {format_time(data[0].time_stamp)} 发送。")
                else:
                    result.append(f"第 {count + 1} 张图片不是火星图哦~")
            try:
                await query.finish("\n".join(result))
            except ActionFailed as e:
                logger.exception(
                    f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}')
                return
    else:
        logger.warning("Not supported: outdated image.")
        return


@summary.handle()
async def _(bot: Bot, event: Event):
    if isinstance(event, GroupMessageEvent):
        if data := ImageMessage.select().where(ImageMessage.group_id == event.group_id).order_by(ImageMessage.image_md5):
            counter = Counter([d.image_md5 for d in data])
            msgs = list()
            count = 1
            for k, v in dict(sorted(counter.items(), key=lambda x: x[1], reverse=True)[
                    :len(counter) if len(counter) < 5 else 5]).items():
                first_sender, time_stamp = [
                    (i.user_id, i.time_stamp) for i in data if i.image_md5 == k][0]
                sender_info = await bot.get_group_member_info(group_id=event.group_id, user_id=first_sender)
                msgs.append(Message("\n".join([
                    str(MessageSegment.image(k)),
                    f"本群第 {count} 位火星图",
                    f"已在本群出现了 {v} 次",
                    f"由 {sender_info['card'] or sender_info['nickname']} 最早在 {format_time(time_stamp)} 发送。"
                ])))
                count += 1
            try:
                await bot.send_group_forward_msg(group_id=event.group_id, messages=generate_forward_msg(msgs, self_id=event.self_id))
            except ActionFailed as e:
                logger.exception(
                    f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}')
                return
    else:
        logger.warning("Not supported: outdated image.")
        return
