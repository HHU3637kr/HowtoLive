from __future__ import annotations

from typing import Any, Optional

from agentscope.message import Msg


class OrchestratorAgent:
    """Wraps Orchestrator to participate in a UserAgent-driven loop.

    - When called with None (or non-user msg), it prints a brief greeting
      and returns an assistant Msg to start the loop.
    - When called with a user Msg, it delegates to orchestrator.handle(text)
      and returns the downstream agent's reply Msg.
    """

    def __init__(self, orchestrator, name: str = "howtolive") -> None:
        self.name = name
        self.orchestrator = orchestrator

    def _extract_user_text(self, msg: Any) -> str:
        # Try common accessors from AgentScope Msg
        text: Optional[str] = None
        if hasattr(msg, "get_content_text"):
            try:
                text = msg.get_content_text()
            except Exception:
                text = None
        if text is None and hasattr(msg, "get_text_content"):
            try:
                text = msg.get_text_content()
            except Exception:
                text = None
        if text is None:
            content = getattr(msg, "content", "")
            text = content if isinstance(content, str) else str(content)
        return text or ""

    async def __call__(self, msg: Optional[Msg]):
        if msg is None or getattr(msg, "role", None) != "user":
            greeting = "你好！请直接输入你的问题（输入 exit 退出）。"
            print(greeting)
            # Msg signature expects (name, content, role)
            return Msg(self.name, greeting, "assistant")

        user_text = self._extract_user_text(msg)
        return await self.orchestrator.handle(user_text)


