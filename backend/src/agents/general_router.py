from __future__ import annotations

from pathlib import Path
from typing import Any

from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory

from ..model_factory import build_chat_model
from ..config import LLMConfig
from ..routing_schema import RoutingChoice

# 获取 prompts 目录的绝对路径
_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def build_general_router(llm: LLMConfig) -> ReActAgent:
    bundle = build_chat_model(llm, force_stream=False)
    
    # 使用绝对路径加载 prompt
    prompt_path = _PROMPTS_DIR / "general_router.system.md"
    sys_prompt = prompt_path.read_text(encoding="utf-8")
    
    agent = ReActAgent(
        name="general-router",
        sys_prompt=sys_prompt,
        model=bundle.model,
        formatter=bundle.formatter,
        memory=InMemoryMemory(),
    )

    # Router 保持静默，仅输出结构化 metadata，避免对用户做自然语言回复
    async def _silent_print(*args, **kwargs):
        return None
    setattr(agent, "print", _silent_print)

    # convenience wrapper to call with structured model
    async def route(self: ReActAgent, msg: Any):  # type: ignore
        # strictly structured output; no user-facing prints
        return await self(msg, structured_model=RoutingChoice)

    setattr(agent, "route", route.__get__(agent, ReActAgent))  # bind method
    return agent


