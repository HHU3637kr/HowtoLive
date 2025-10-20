from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from agentscope.message import Msg
from agentscope.session import SessionBase


class HowtoLiveSession(SessionBase):
    """Session implementation based on AgentScope SessionBase.

    Features:
    - user_id -> session_id directory layout
    - optional compact mode (persist only user/assistant text messages)
    - optional skip for router agent
    """

    def __init__(
        self,
        save_dir: str = "backend/.sessions",
        *,
        include_router: bool = False,
        compact: bool = False,
        max_messages_per_agent: int = 12,
    ) -> None:
        # SessionBase may not define an __init__ that accepts parameters in some versions.
        # We set save_dir directly to remain compatible.
        self.save_dir = save_dir
        self.include_router = include_router
        self.compact = compact
        self.max_messages_per_agent = max_messages_per_agent

    # --- path helpers ---
    def _state_path(self, session_id: str, user_id: Optional[str]) -> str:
        # New layout: backend/.sessions/{user_id}/{session_id}/state.json
        if user_id:
            return os.path.join(self.save_dir, user_id, session_id, "state.json")
        return os.path.join(self.save_dir, session_id, "state.json")

    def _timeline_path(self, session_id: str, user_id: Optional[str]) -> str:
        # New layout: backend/.sessions/{user_id}/{session_id}/timeline.json
        if user_id:
            return os.path.join(self.save_dir, user_id, session_id, "timeline.json")
        return os.path.join(self.save_dir, session_id, "timeline.json")

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # --- compact helpers ---
    def _extract_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts: List[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                    texts.append(str(item.get("text")))
            return "\n".join(texts)
        return str(content)

    async def _memory_to_compact(self, agent: Any) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        try:
            mem_list = await agent.memory.get_memory()
        except Exception:
            return result
        for m in mem_list:
            role = getattr(m, "role", None)
            if role not in ("user", "assistant"):
                continue
            name = getattr(m, "name", None) or (agent.name if role == "assistant" else "user")
            text: Optional[str] = None
            if hasattr(m, "get_content_blocks"):
                try:
                    blocks = m.get_content_blocks("text")
                    if isinstance(blocks, list) and blocks:
                        text = "\n".join([b.get("text") if isinstance(b, dict) else str(b) for b in blocks])
                except Exception:
                    text = None
            if text is None:
                text = self._extract_text(getattr(m, "content", ""))
            if not text:
                continue
            result.append({"role": role, "name": name, "text": text})
        if len(result) > self.max_messages_per_agent:
            result = result[-self.max_messages_per_agent :]
        return result

    async def _compact_to_memory(self, agent: Any, messages: List[Dict[str, Any]]) -> None:
        try:
            await agent.memory.clear()
        except Exception:
            return
        for item in messages:
            role = item.get("role")
            text = item.get("text", "")
            name = item.get("name") or (agent.name if role == "assistant" else "user")
            if role and text:
                # Msg signature: (name, content, role)
                await agent.memory.add(Msg(name, text, role))

    # --- SessionBase interface ---
    async def save_session_state(self, *, session_id: str, user_id: Optional[str] = None, strict: bool = True, **state_modules: Any) -> None:  # type: ignore[override]
        path = self._state_path(session_id, user_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        agents_payload: Dict[str, Any] = {}
        for name, module in state_modules.items():
            if not self.include_router and name == "general-router":
                continue
            if self.compact:
                agents_payload[name] = {"messages": await self._memory_to_compact(module)}
            else:
                try:
                    agents_payload[name] = module.state_dict()
                except Exception:
                    # best-effort: skip modules that cannot be serialized
                    pass

        payload = {"user_id": user_id, "session_id": session_id, "agents": agents_payload}
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)

    async def load_session_state(self, *, session_id: str, user_id: Optional[str] = None, strict: bool = True, **state_modules: Any) -> None:  # type: ignore[override]
        path = self._state_path(session_id, user_id)
        if not os.path.exists(path):
            # Fallback to legacy single-file layout if present
            legacy = os.path.join(self.save_dir, user_id or "", f"{session_id}.state.json")
            if os.path.exists(legacy):
                path = legacy
            else:
                legacy2 = os.path.join(self.save_dir, user_id or "", f"{session_id}.json")
                if os.path.exists(legacy2):
                    path = legacy2
                else:
                    return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        states = data.get("agents", {})
        for name, module in state_modules.items():
            state = states.get(name)
            if state is None:
                continue
            if self.compact and isinstance(state, dict) and "messages" in state:
                await self._compact_to_memory(module, state.get("messages", []))
                continue
            try:
                module.load_state_dict(state, strict=strict)
            except Exception:
                try:
                    module.load_state_dict(state, strict=False)
                except Exception:
                    pass

    # --- Timeline (ordered log) API ---
    async def append_events(self, *, session_id: str, user_id: Optional[str], events: List[Dict[str, Any]]) -> None:
        """Append ordered events to a single timeline array.

        Event schema (minimal):
          - type: "message" | "route" | ...
          - agent: str
          - role: "user" | "assistant" | "system"
          - text: str (for message)
          - structured: dict (for route)
          - ts: iso8601 (filled if missing)
          - seq: int (filled automatically)
        """
        path = self._timeline_path(session_id, user_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        blob: Dict[str, Any]
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    blob = json.load(f)
            except Exception:
                blob = {}
        else:
            blob = {}

        if not isinstance(blob, dict):
            blob = {}
        blob.setdefault("user_id", user_id)
        blob.setdefault("session_id", session_id)
        blob.setdefault("version", "1.0")
        timeline = blob.get("timeline")
        if not isinstance(timeline, list):
            timeline = []

        # determine next seq
        next_seq = 1
        if timeline:
            last = timeline[-1]
            if isinstance(last, dict) and isinstance(last.get("seq"), int):
                next_seq = last["seq"] + 1

        # normalize and append
        for ev in events:
            ev = dict(ev) if isinstance(ev, dict) else {}
            if "ts" not in ev:
                ev["ts"] = self._now_iso()
            ev["seq"] = next_seq
            next_seq += 1
            timeline.append(ev)

        blob["timeline"] = timeline
        blob["stats"] = {"num_events": len(timeline)}

        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(blob, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)


