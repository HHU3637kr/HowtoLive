from __future__ import annotations

from pathlib import Path
from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit

from ..model_factory import build_chat_model
from ..config import LLMConfig

# 获取 prompts 目录的绝对路径
_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def build_general_answer(
    llm: LLMConfig,
    *,
    long_term_memory=None,
    ltm_mode: str = "agent_control",
) -> ReActAgent:
    bundle = build_chat_model(llm)  # use default streaming from YAML
    
    # 使用绝对路径加载 prompt
    prompt_path = _PROMPTS_DIR / "general_answer.system.md"
    sys_prompt = prompt_path.read_text(encoding="utf-8")
    
    agent = ReActAgent(
        name="general",
        sys_prompt=sys_prompt,
        model=bundle.model,
        formatter=bundle.formatter,
        memory=InMemoryMemory(),
        toolkit=Toolkit(),
        long_term_memory=long_term_memory,
        long_term_memory_mode=ltm_mode,
    )
    return agent


