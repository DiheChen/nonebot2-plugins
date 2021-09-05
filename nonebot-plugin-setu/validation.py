"""
 - Author: DiheChen
 - Date: 2021-09-02 11:12:21
 - LastEditTime: 2021-09-04 17:37:32
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from typing import List, Literal, Optional

from pydantic import BaseModel, validator


class RequestData(BaseModel):
    """
    - 数据效验模块
    """
    r18: Literal[0, 1, 2] = 0
    num: int = 1
    uid: Optional[List[int]] = list()
    keyword: str = ""
    tag: Optional[List[List[str]]] = ""
    size: Literal["original", "regular", "small", "thumb", "mini"] = "original"
    proxy: str = ""
    dateAfter: Optional[int] = ""
    dateBefore: Optional[int] = ""
    dsc: bool = False

    @validator("num")
    def check_num(cls, value):
        if not 1 <= value <= 100:
            raise ValueError("Invalid key: num.")
        return value

    @validator("uid")
    def check_uid(cls, value):
        if len(value) > 20:
            raise ValueError("Parameter uid is too long.")
        return value

    @validator("tag")
    def check_tag(cls, value):
        if value:
            for v in value:
                if len(v) > 2:
                    raise ValueError("Invalid key: tag.")
        return value
