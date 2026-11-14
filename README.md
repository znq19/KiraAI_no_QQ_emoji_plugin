# 禁止QQ Emoji

还在为哪怕人设提示词里写了禁止发送 emoji，自己的 bot 还在频繁发送 QQ 黄豆表情、显得非常人机而让你想 😓 吗？那么快安装本插件吧。

> **注意**：本插件只负责不让 bot 发 **QQ emoji**，而非所有的 emoji。
> 后者在我看来偶尔作为表达方式还是不错的，且人设提示词里可以较好抑制。
> 主要原因是前者在 bot 眼里被 KiraAI 框架注册成了一个独立标签（`<emoji>`），
> 看起来更像「表情包」而不是通常意义上的 emoji，所以提示词约束往往压不住它。

## 它做什么

在每轮 LLM 请求时，从输出的标签表中移除 `<emoji>` 标签。
模型看不到这个标签，自然就不会再输出 QQ 黄豆表情。

## 它不做什么

| 能力 | 是否受影响 |
|---|---|
| 发送表情包（sticker） | ❌ 不受影响 |
| 戳一戳 / @ / 图片 / 语音 / 文件 / 转发 | ❌ 不受影响 |
| 识别用户发来的 QQ emoji | ❌ 不受影响 |
| 识别用户发来的贴表情 | ❌ 不受影响 |
| 模型直接输出 Unicode 表情（😀🥺） | ⚠️ 仍可输出，本插件不管这个 |

## 安装

1. 下载本仓库，把 `KiraAI_no_QQ_emoji_plugin/` 整个目录放进 KiraAI 的 `data/plugins/` 下
2. 重启 KiraAI（或从 WebUI 插件页重新加载）
3. 确认插件列表中「禁止QQ Emoji」为已启用

## 配置

只有一项：`enabled`（默认开启）。切换后**即时生效，无需重启**。

## 兼容性

- 需要 KiraAI `>= 3.0.0`
- 基于 `@on.llm_request` + `TagSet` 实现，不修改任何全局状态
- 停用插件后 emoji 立即恢复，不存在不可逆的副作用

## 实现说明

```python
@on.llm_request(priority=Priority.MEDIUM)
async def strip_emoji_tag(self, event, _request, tag_set):
    tag_set.unregister("emoji")
```

`TagSet` 每轮请求新建，因此该操作天然幂等、完全可逆；
钩子按优先级降序执行，`MEDIUM < SYS_HIGH`，保证在内置插件注册 emoji 标签之后、
格式提示词渲染之前完成摘除。

## License

本项目采用 **GNU Affero General Public License v3.0（AGPL-3.0）** 授权，详见 [LICENSE](LICENSE)。

> AGPL-3.0 是强传染性协议：如果你修改了本插件并通过网络向他人提供服务，
> 你有义务以相同协议公开你修改后的源码。请在使用前确认这一点符合你的预期。
