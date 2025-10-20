from __future__ import annotations

from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit

from ..model_factory import build_chat_model
from ..config import LLMConfig


def build_howtocook(
    llm: LLMConfig,
    *,
    long_term_memory=None,
    ltm_mode: str = "agent_control",
    toolkit: Toolkit | None = None,
) -> ReActAgent:
    """构建烹饪助手 Agent
    
    Args:
        llm: LLM 配置
        long_term_memory: 长期记忆实例
        ltm_mode: 长期记忆模式
        toolkit: 工具集（如果传入，则使用；否则创建空的）
    """
    bundle = build_chat_model(llm)
    
    # 如果没有传入 toolkit，创建空的
    if toolkit is None:
        toolkit = Toolkit()
    
    agent = ReActAgent(
        name="howtocook",
        sys_prompt=open("backend/src/prompts/howtocook.system.md", "r", encoding="utf-8").read(),
        model=bundle.model,
        formatter=bundle.formatter,
        memory=InMemoryMemory(),
        toolkit=toolkit,
        long_term_memory=long_term_memory,
        long_term_memory_mode=ltm_mode,
    )
    return agent


