from __future__ import annotations

from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit

from ..model_factory import build_chat_model
from ..config import LLMConfig


def build_general_answer(
    llm: LLMConfig,
    *,
    long_term_memory=None,
    ltm_mode: str = "agent_control",
) -> ReActAgent:
    bundle = build_chat_model(llm)  # use default streaming from YAML
    agent = ReActAgent(
        name="general",
        sys_prompt=open("backend/src/prompts/general_answer.system.md", "r", encoding="utf-8").read(),
        model=bundle.model,
        formatter=bundle.formatter,
        memory=InMemoryMemory(),
        toolkit=Toolkit(),
        long_term_memory=long_term_memory,
        long_term_memory_mode=ltm_mode,
    )
    return agent


