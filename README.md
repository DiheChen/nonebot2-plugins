<p align="center">
  <a href="#"><img src="https://raw.githubusercontent.com/nonebot/nonebot2/master/docs/.vuepress/public/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot2-plugins

_✨ ~~女生自用~~ nonebot2 插件。 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/Chendihe4975/nonebot2-plugins/master/LICENSE">
    <img src="https://img.shields.io/github/license/Chendihe4975/nonebot2-plugins.svg" alt="license">
  </a>
  <a href="https://pypi.org/project/nonebot2/">
    <img src="https://img.shields.io/badge/nonebot-2.0.0.a15+-red.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</p>


## 目前功能

- nonebot-plugin-describeinstances 实体信息查询

  > 接口来自 [腾讯云 自然语言处理 实体信息查询](https://cloud.tencent.com/document/api/271/39420) , 需自行前往 [腾讯云 API 密钥管理](https://console.cloud.tencent.com/capi)  新建密钥
  >
  > 并在 nonebot 的配置文件 `.env.{environment}` 填入 `secret_id` 和 `secret_key` 。

- nonebot-plugin-ocr ocr文字识别

- nonebot-plugin-outdated_image 火星图统计

  > 注意事项请见 [注释](https://github.com/Chendihe4975/nonebot2-plugins/blob/master/nonebot-plugin-outdated_image/__init__.py#L44) 。

- nonebot-plugin-epic_reminder Epic 白嫖提醒小助手

  > Linux 玩家需自行将微软雅黑的字体文件 `msyh.ttc` 复制到插件目录下
  >
  > 也可使用其它字体, 见 [draw_image.py](https://github.com/Chendihe4975/nonebot2-plugins/blob/master/nonebot-plugin-epic_reminder/draw_image.py#L27)。
  >
  > Pillow >= 8.2.0

- nonebot-plugin-setu 群内活跃气氛小助手

  > 接口来自 [Lolicon API](https://api.lolicon.app/) , 主要功能: 发涩图, 附带功能: 反向代理 i.pximg.net 。
  >
  > 配置项较为复杂, 见 [README](https://github.com/Chendihe4975/nonebot2-plugins/tree/master/nonebot-plugin-setu) 。
  >
  > 附带功能需开放公网访问, 可能会有憨批拿爬虫搁那 CC,  服务器上行被占满之后 websocket 连接可能会断。
  >
  > 可使用 反向代理 / CDN 增强安全性, 公用 Bot 可以考虑放弃该附带功能。

## 如何使用

下载你中意的插件, 按常规方法添加到你的 nonebot2 机器人上。

## 特别感谢

- [nonebot / nonebot2](https://github.com/nonebot/nonebot2)
- [Mrs4s / go-cqhttp](https://github.com/Mrs4s/go-cqhttp)

## 优化建议

如有优化建议请积极提交 Issues 或 Pull requests。

如果你要提交 Pull requests, 请确保你的代码风格和项目已有的代码保持一致。

![](https://i.loli.net/2021/08/23/5Je1CzgoGmqAI3V.jpg)