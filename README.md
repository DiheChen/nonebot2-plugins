# nonebot2-plugins
~~女生自用~~ nonebot2 插件。

## 目前功能

- nonebot-plugin-describeinstances 实体信息查询

  > 接口来自 [腾讯云 自然语言处理 实体信息查询](https://cloud.tencent.com/document/api/271/39420) , 需自行前往 [腾讯云 API 密钥管理](https://console.cloud.tencent.com/capi)  新建密钥
  >
  > 并在 nonebot 的配置文件 `.env.{environment}` 填入 `secret_id` 和 `secret_key` 。

- nonebot-plugin-ocr ocr文字识别

- nonebot-plugin-outdated_image 火星图统计

- nonebot-plugin-epic_reminder Epic 白嫖提醒小助手

  > Linux 玩家需自行将微软雅黑的字体文件 `msyh.ttc` 复制到插件目录下
  >
  > 也可使用其它字体, 见 [draw_image.py](https://github.com/Chendihe4975/nonebot2-plugins/blob/master/nonebot-plugin-epic_reminder/draw_image.py#L27)。

## 如何使用

下载你中意的插件, 按常规方法添加到你的 nonebot2 机器人上。

## 特别感谢

- [nonebot / nonebot2](https://github.com/nonebot/nonebot2)
- [Mrs4s / go-cqhttp](https://github.com/Mrs4s/go-cqhttp)

## 优化建议

如有优化建议请积极提交 Issues 或 Pull requests。

![](https://i.loli.net/2021/08/23/5Je1CzgoGmqAI3V.jpg)