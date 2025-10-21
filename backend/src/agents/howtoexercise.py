from __future__ import annotations

from pathlib import Path
from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit

from ..model_factory import build_chat_model
from ..config import LLMConfig

# 获取 prompts 目录的绝对路径
_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def build_howtoexercise(
    llm: LLMConfig,
    *,
    long_term_memory=None,
    ltm_mode: str = "agent_control",
    toolkit: Toolkit | None = None,
    knowledge=None,  # AgentKnowledgeBase 实例
) -> ReActAgent:
    """构建运动助手 Agent
    
    Args:
        llm: LLM 配置
        long_term_memory: 长期记忆实例
        ltm_mode: 长期记忆模式
        toolkit: 工具集（如果传入，则使用；否则创建空的）
        knowledge: Agent 知识库实例
    """
    if toolkit is None:
        toolkit = Toolkit()
    
    # 如果提供了知识库，注册为工具
    if knowledge:
        toolkit.register_tool_function(
            knowledge.retrieve_knowledge,
            func_description="搜索运动训练领域的知识库。当用户询问专业知识、方法、技巧时使用。",
        )
        toolkit.register_tool_function(
            knowledge.add_knowledge_to_user,
            func_description="将重要的运动经验添加到个人知识库。仅在用户分享有价值的经验、笔记时使用。",
        )
    
    bundle = build_chat_model(llm)
    
    # 使用绝对路径加载 prompt
    prompt_path = _PROMPTS_DIR / "howtoexercise.system.md"
    sys_prompt = prompt_path.read_text(encoding="utf-8")
    
    agent = ReActAgent(
        name="howtoexercise",
        sys_prompt=sys_prompt,
        model=bundle.model,
        formatter=bundle.formatter,
        memory=InMemoryMemory(),
        toolkit=toolkit,
        long_term_memory=long_term_memory,
        long_term_memory_mode=ltm_mode,
    )
    return agent


