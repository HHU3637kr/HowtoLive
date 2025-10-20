from __future__ import annotations

from typing import Dict

from agentscope.message import Msg

from .routing_schema import RoutingChoice
from .session_adapter import HowtoLiveSession


class Orchestrator:
    def __init__(self, general_router, general_answer, domain_agents: Dict[str, object], *,
                 user_id: str | None = None, session_id: str | None = None,
                 session: HowtoLiveSession | None = None) -> None:
        self.general_router = general_router
        self.general_answer = general_answer
        self.domain_agents = domain_agents
        self.user_id = user_id or "anonymous"
        self.session_id = session_id or "default"
        self.session = session or HowtoLiveSession(compact=True, include_router=False)

    async def restore(self) -> None:
        """Load states for all agents if any (must be called once at startup)."""
        agents = {"general-router": self.general_router, "general": self.general_answer}
        agents.update(self.domain_agents)
        await self.session.load_session_state(session_id=self.session_id, user_id=self.user_id, **agents)

    async def handle(self, user_text: str):
        msg_user = Msg("user", user_text, "user")
        # 显式路由：强制结构化
        router_res = await self.general_router(msg_user, structured_model=RoutingChoice)
        choice = (router_res.metadata or {}).get("your_choice", "general")

        if choice in ("general", "none"):
            reply = await self.general_answer(msg_user)
        else:
            agent = self.domain_agents.get(choice)
            if not agent:
                reply = await self.general_answer(msg_user)
            else:
                reply = await agent(msg_user)

        # save session state after each round (agent states)
        agents = {"general-router": self.general_router, "general": self.general_answer}
        agents.update(self.domain_agents)
        await self.session.save_session_state(session_id=self.session_id, user_id=self.user_id, **agents)

        # append ordered timeline events (single time axis)
        def _extract_text(m: Msg) -> str:
            text = None
            if hasattr(m, "get_content_blocks"):
                try:
                    blocks = m.get_content_blocks("text")
                    if isinstance(blocks, list) and blocks:
                        text = "\n".join([b.get("text") if isinstance(b, dict) else str(b) for b in blocks])
                except Exception:
                    text = None
            if text is None:
                content = getattr(m, "content", None)
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    parts = [str(it.get("text")) for it in content if isinstance(it, dict) and "text" in it]
                    text = "\n".join(parts) if parts else ""
                else:
                    text = str(content or "")
            return text or ""

        # ensure first round also logs the user message; always append user input first
        events = [
            {"type": "message", "agent": "user", "role": "user", "text": user_text},
            {"type": "route", "agent": "general-router", "role": "assistant", "structured": router_res.metadata or {}},
        ]
        events.append({
            "type": "message",
            "agent": getattr(reply, "name", None) or choice,
            "role": "assistant",
            "text": _extract_text(reply),
        })
        await self.session.append_events(session_id=self.session_id, user_id=self.user_id, events=events)
        return reply


