"""
 - Author: DiheChen
 - Date: 2021-09-01 17:48:22
 - LastEditTime: 2021-09-05 14:43:11
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from pydantic import BaseModel


class Config(BaseModel):
    """
    - ·auto_fetch` : 自动缓存图片
    - `global_r18` : 全局 r18 开关, 禁用后 Bot 将不发送 r18 图片
    - `recall_time` : 经过多少秒后撤回图片, 设置成 0 时候不自动撤回
    - `url_only` : 仅回复 url , 不发送图片
    - `online_mode_pure` 纯在线模式, 该模式下 Bot 将不会缓存图片到本地
    - `use_forward` : 启用合并转发
    - `proxy`: 代理服务器地址, 仅支持 http 代理
    - `public_address` : Bot 对外开放的地址, 若已设置反向代理, 该项应该填反向代理后的地址
    - `single_image_limit` : 限制单次发送色图数量
    """
    auto_fetch: int
    global_r18: bool
    recall_time: int
    online_mode_pure: bool
    url_only: bool
    use_forward: bool
    proxy: str
    reverse_proxy: str
    public_address: str
    single_image_limit: int


setting = {
    "auto_fetch": 0,
    "global_r18": True,
    "recall_time": 0,
    "online_mode_pure": False,
    "url_only": False,
    "use_forward": True,
    "proxy": "",
    "reverse_proxy": "",
    "public_address": "http://127.0.0.1:8080",
    "single_image_limit": 10
}

config = Config(**setting)
