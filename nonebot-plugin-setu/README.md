# nonebot-plugin-setu

nonebot-plugin-setu 配置说明。

## 配置

自定义配置请修改 [config.py #L35](https://github.com/Chendihe4975/nonebot2-plugins/blob/master/nonebot-plugin-setu/config.py#L35),

  - `auto_fetch` : 自动缓存图片

  - `global_r18` : 全局 r18 开关, 禁用后 Bot 将不发送 r18 图片

  - `recall_time` : 经过多少秒后撤回图片, 设置成 0 时候不自动撤回

  - `url_only` : 仅回复 url , 不发送图片

  - `online_mode_pure` 纯在线模式, 该模式下 Bot 将不会缓存图片到本地

  - `use_forward` : 启用合并转发

  - `proxy`: 代理服务器地址, 仅支持 http 代理

  - `public_address` : Bot 对外开放的地址, 若已设置反向代理, 该项应该填反向代理后的地址

  - `single_image_limit` : 限制单次发送色图数量

### public_address

要使用此项, 请在有公网 ip 的服务器上运行你的机器人, 如果你坚持在本地计算机运行, 请使用内网穿透。

我们知道 i.pximg.net 具有防盗链措施, 请求头中不含 `"Referer": "https://www.pixiv.net"` 会返回 403, 于是我们准备自己搭建一个反代服务 ( 能自建为什么要用别人的 ? ) 。

我们先来打开一张图片 ( SFW ):

>  https://i.pximg.net/img-original/img/2021/02/24/18/16/59/88019201_p0.jpg

你会看到大大的 403 Forbidden。

我们启动我们的 NoneBot2, 并使该插件被 Bot 加载, 假设我们的 Bot 是运行在 8080 端口上的, 将图片链接中的 `https://i.pximg.net/` 修改为 `http://127.0.0.1:8080/pixiv/` , 得到以下链接

> http://127.0.0.1:8080/pixiv/img-original/img/2021/02/24/18/16/59/88019201_p0.jpg

如果我们在 NoneBot 运行的服务器上访问这个链接, 是可以访问到图片的, 但是我们需要让别人也能通过链接访问到你的反代服务的话, 你需要:

- 将 NoneBot 监听的 `HOST` 修改为 `0.0.0.0`
- 在服务器的防火墙面板里, 打开 8080 端口 ( 如果你的 Bot 是运行在 8080 端口上的话 )
- 为你的 OneBot 协议端及 NoneBot 设置 access_token, 防止入侵

这样的话, 别人访问以下地址也能得到图片:

> http://{你服务器的公网 ip}:8080/pixiv/img-original/img/2021/02/24/18/16/59/88019201_p0.jpg

如果你这样做, 会直接暴露服务的端口, 无法使用加密通信等, 更建议你使用 Nginx, Apache 之类的 Web Server 设置反代, 

最后在本插件的配置文件里面修改为 `"public_address": "http://{服务器 ip}:{机器人端口}"` ( 没设置反代的情况下 )或 `"public_address": "https://{你的域名}"` ( 设置了反代的情况下 )。

### proxy

如果你不能直连 `i.pximg.net`, 你需要借助魔法, 如果你的魔法在 1080 端口上, 请在本插件的配置文件里面填入 `"proxy": "http://127.0.0.1:1080"` 。

### online_mode_pure

纯在线模式, 设定为 True 后不会讲图片保存到本地, 为了确保该模式可用, 你需要先配置好 `public_address`

OneBot 协议端将收到以下调用:

```json
{
    "type": "image",
    "data": {
        "file": "http://{你服务器的 ip}:{NoneBot 端口}/pixiv/img-original/img/2021/02/24/18/16/59/88019201_p0.jpg"
    }
}
```

或者

```json
{
    "type": "image",
    "data": {
        "file": "http://{你的域名}/pixiv/img-original/img/2021/02/24/18/16/59/88019201_p0.jpg"
    }
}
```

本插件不考虑使用 `base64` 发送图片。

### url_only

仅回复图片 url ( 你反代过的 ), 不发送图片, 极高响应速度, 不用怕 ghs 被封号。

你没搞好 `public_address` 别人可能打不开。

## single_image_limit

限制单次发送色图数量, 默认为 10, 可调整为 1 - 100 之间的任意整数。

### auto_fetch

url_only 及 online_mode_pure 均设定为 False 的时候, 可以设定 auto_fetch 为 1 - 100 任意正整数使机器人每隔半小时自动缓存该数量的图片。