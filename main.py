"""禁止QQ Emoji — 在标签层摘除 <emoji>，面向 KiraAI >= 3.0.0。

原理：只从「本轮 TagSet」中注销 emoji 标签，绝不修改任何全局状态
（适配器能力列表 / adapter 的 _supported_elements / 事件 supported_elements）。

效果边界：
- 生效：LLM 输出格式提示里不再出现 <emoji> 标签 ⇒ 模型不再主动发 QQ 黄豆表情
- 不影响接收：用户发的 QQ emoji(face) 与 贴表情(image/Sticker) 照常解析进上下文
- 不影响其它能力：text/at/img/record/sticker/poke/file/video/forward 全部保留
- 完全可逆：每轮 TagSet 都是新建的；插件停用后 emoji 立即恢复，无需重启
- 平台无关：作用于 <emoji> 标签本身，凡声明了 emoji 能力的适配器都会生效

若模型仍执意输出 <emoji>，框架 parse_xml 会静默忽略未注册的标签，不报错；
某条 <msg> 只剩表情时该条不发送，不会产生空消息。
"""

from core.chat.message_utils import KiraMessageBatchEvent
from core.plugin import BasePlugin, Priority, logger, on
from core.tag import TagSet


class NoEmojiPlugin(BasePlugin):
    async def initialize(self):
        if self.plugin_cfg.get("enabled", True):
            logger.info("NoQQEmoji: <emoji> tag will be stripped from every LLM request")
        else:
            logger.info("NoQQEmoji: enabled=false, <emoji> tag left intact")

    async def terminate(self):
        # No global mutation happened, so there is nothing to restore.
        pass

    @on.llm_request(priority=Priority.MEDIUM)
    async def strip_emoji_tag(self, event: KiraMessageBatchEvent, _request, tag_set: TagSet):
        """Remove the emoji tag right after builtin tag injection.

        Handlers run in descending priority order. Builtin plugins register the
        tag at SYS_HIGH and SYS_HIGH - 1, so MEDIUM runs after them and before
        the format prompt is rendered. Nothing between MEDIUM and the render
        step registers tags, so this is the correct and sufficient slot.
        """
        if not self.plugin_cfg.get("enabled", True):
            return
        tag_set.unregister("emoji")
