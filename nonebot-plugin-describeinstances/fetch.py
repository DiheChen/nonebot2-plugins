"""
 - Author: DiheChen
 - Date: 2021-08-23 09:59:04
 - LastEditTime: 2021-08-24 05:07:13
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from base64 import b64encode
from hashlib import sha1
from hmac import new
from random import randint
from time import time
from typing import Any, Dict, Union

from aiohttp import ClientSession
from loguru import logger

try:
    import ujson as json
except:
    import json

from .config import Config
from .data import DescribeInstances


def get_signature(params: dict) -> str:
    sign_str = "GET" + "nlp.tencentcloudapi.com/" + "?" + \
        "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    hashed = new(bytes(Config.secret_key, "utf-8"),
                 bytes(sign_str, "utf-8"), sha1).digest()
    signature = b64encode(hashed)
    return signature.decode()


async def fetch_data(instances: str) -> Union[str, Dict]:
    params = {
        "Action": "DescribeEntity",
        "Version": "2019-04-08",
        "Region": "ap-guangzhou",
        "EntityName": instances,
        "Timestamp": int(time()),
        "Nonce": randint(1, int(1e9)),
        "SecretId": Config.secret_id,
    }
    params["Signature"] = get_signature(params)
    try:
        async with ClientSession() as session:
            async with session.get("https://nlp.tencentcloudapi.com/", params=params, verify_ssl=False) as resp:
                if "Error" in (data := await resp.json())["Response"]:
                    return data["Response"]["Error"]["Message"]
                return json.loads(data["Response"]["Content"])
    except Exception as e:
        logger.exception(e)
        return str(e)


def processing_data(data: Any) -> str:
    if isinstance(data, dict):
        DescribeInstances.replace(
            instances=data["名称"][0]["Name"],
            instances_en=data["英文名"][0]["Name"] if "英文名" in data else data["Name"][0]["Name"],
            describe=data["简介"][0]["Name"] if "简介" in data else data["Foundin"][0]["Name"]
        ).execute()
        data = data["简介"][0]["Name"] if "简介" in data else data["Foundin"][0]["Name"]
    return str(data)
