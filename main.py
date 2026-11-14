"""禁止Emoji — KiraAI v3.x 兼容实现（面向 v3.2.0-beta.1 审计通过）

原理：只从「本轮 TagSet」中注销 emoji 标签，绝不修改任何全局状态
（适配器能力列表 / adapter 的 _supported_elements / 事件 supported_elements）。

效果边界：
- 生效：LLM 输出格式提示里不再出现 <emoji> 标签 ⇒ 模型不会再发 QQ 表情
- 不影响接收：用户发的 QQ emoji(face) 与 贴表情(image/Sticker) 照常解析进上下文
- 不影响其它能力：text/at/img/record/sticker/poke/file/video/forward 全部保留
- 完全可逆：每轮 TagSet 都是新建的；插件停用后 emoji 立即恢复，无需重启
"""

from core.chat.message_utils import KiraMessageBatchEvent
from core.plugin import BasePlugin, Priority, logger, on
from core.tag import TagSet


class NoEmojiPlugin(BasePlugin):
    async def initialize(self):
        if self.plugin_cfg.get("enabled", True):
            logger.info("NoEmoji: <emoji> tag will be stripped from every LLM request")
        else:
            logger.info("NoEmoji: enabled=false, <emoji> tag left intact")

    async def terminate(self):
        # No global mutation happened, so there is nothing to restore.
        pass

    @on.llm_request(priority=Priority.MEDIUM)
    async def strip_emoji_tag(self, event: KiraMessageBatchEvent, _request, tag_set: TagSet):
        """Remove the emoji tag right after builtin tag injection.

        Handlers run in descending priority order, so MEDIUM runs after the
        builtin kira-ai plugin (SYS_HIGH) registered the emoji tag, and still
        before the format prompt is rendered.
        """
        if not self.plugin_cfg.get("enabled", True):
            return
        tag_set.unregister("emoji")
