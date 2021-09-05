"""
 - Author: DiheChen
 - Date: 2021-06-29 23:16:20
 - LastEditTime: 2021-08-23 17:45:50
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from loguru import logger
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, MessageEvent
from nonebot.exception import ActionFailed
from nonebot.plugin import on_command
from nonebot.typing import T_State

ocr = on_command("ocr", priority=5, block=True)


@ocr.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        if event.raw_message != "ocr":
            state['image'] = event.raw_message
    else:
        logger.warning("Not support: ocr.")
        return


@ocr.got('image', prompt='请发送图片, 支持多张。')
async def _(bot: Bot, event: Event):
    if isinstance(event, MessageEvent):
        result = [f"> {event.sender.card or event.sender.nickname}"]
        image_list = [s.data['file']
                      for s in event.message if s.type == 'image' and 'file' in s.data]
        for count, i in enumerate(image_list):
            texts = (await bot.call_api("ocr_image", image=i))["texts"]
            result.append(
                f"第 {count + 1} 张图片的识别结果是: {''.join([i['text'] for i in texts])}")
        try:
            await ocr.finish("\n".join(result))
        except ActionFailed as e:
            logger.exception(
                f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
            )
            return
    else:
        logger.warning("Not support: ocr.")
        return
