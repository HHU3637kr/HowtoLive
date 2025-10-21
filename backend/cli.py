from __future__ import annotations

import asyncio
import os
import sys
import uuid

# Ensure project root is on sys.path when executed as a script (python backend/main.py)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from backend.src.config import load_app_config
from backend.src.agents.general_router import build_general_router
from backend.src.agents.general_answer import build_general_answer
from backend.src.agents.howtoeat import build_howtoeat
from backend.src.agents.howtocook import build_howtocook
from backend.src.agents.howtoexercise import build_howtoexercise
from backend.src.agents.howtosleep import build_howtosleep
from backend.src.agents.orchestrator_agent import OrchestratorAgent
from backend.src.orchestrator import Orchestrator
from backend.src.long_term_memory import build_mem0_long_term_memory
from backend.src.logged_long_term_memory import wrap_with_logging
from backend.src.mcp_manager import MCPManager
from backend.src.rag_manager import RAGManager


async def main() -> None:
    cfg = load_app_config("backend/config")

    general_router = build_general_router(cfg.llm)

    # ask identity
    print("howtolive CLI（显式路由版）。输入 'exit' 退出。\n")
    user_id = input("请输入 user_id（默认 anonymous）：").strip() or "anonymous"

    # Build long-term memory for this user if enabled
    user_ltm = build_mem0_long_term_memory(cfg.ltm, cfg.llm, user_id=user_id)
    
    # 为长期记忆添加日志包装（方便追踪 static_control 模式下的记忆操作）
    user_ltm = wrap_with_logging(user_ltm)
    
    # 初始化 MCP 管理器（负责工具注册和分组）
    mcp_manager = None
    if cfg.mcp and cfg.mcp.servers:
        try:
            print("\n[MCP] 初始化 MCP 服务...")
            mcp_manager = MCPManager(cfg.mcp)
            await mcp_manager.initialize()
            print("[MCP] ✓ MCP 服务初始化完成\n")
        except Exception as e:
            print(f"[MCP] ✗ MCP 初始化失败: {e}\n")
            mcp_manager = None
    
    # 初始化 RAG 管理器（负责知识库管理）
    rag_manager = None
    if cfg.rag and cfg.rag.enabled:
        try:
            print("\n")
            rag_manager = RAGManager(cfg.rag)
            await rag_manager.initialize()
            print()
        except Exception as e:
            print(f"[RAG] ✗ RAG 初始化失败: {e}\n")
            rag_manager = None

    general_answer = build_general_answer(cfg.llm, long_term_memory=user_ltm, ltm_mode=(cfg.ltm.mode if (cfg.ltm and cfg.ltm.enabled) else "agent_control"))

    # 为每个 Agent 创建知识库和工具集
    ltm_mode = cfg.ltm.mode if (cfg.ltm and cfg.ltm.enabled) else "agent_control"
    
    domain_agents = {}
    for agent_name in ["howtoeat", "howtocook", "howtosleep", "howtoexercise"]:
        # 创建 Toolkit（可能包含 MCP 工具）
        toolkit = None
        if mcp_manager and agent_name == "howtocook":
            toolkit = mcp_manager.get_toolkit("howtocook")
        
        # 获取 Agent 的知识库
        agent_kb = None
        if rag_manager:
            agent_kb = rag_manager.get_agent_kb(agent_name, user_id)
        
        # 构建 Agent
        build_func = {
            "howtoeat": build_howtoeat,
            "howtocook": build_howtocook,
            "howtosleep": build_howtosleep,
            "howtoexercise": build_howtoexercise,
        }[agent_name]
        
        agent = build_func(
            cfg.llm,
            long_term_memory=user_ltm,
            ltm_mode=ltm_mode,
            toolkit=toolkit,
            knowledge=agent_kb,
        )
        
        domain_agents[agent_name] = agent

    # list existing sessions for this user and allow selection (new directory layout)
    sessions_dir = os.path.join(_CURRENT_DIR, ".sessions", user_id)
    existing = []
    if os.path.isdir(sessions_dir):
        for fn in os.listdir(sessions_dir):
            full = os.path.join(sessions_dir, fn)
            if os.path.isdir(full):
                # session_id directories
                existing.append(fn)
    session_id = None
    if existing:
        print("检测到已有会话：")
        for i, sid in enumerate(existing):
            print(f"  [{i}] {sid}")
        choice = input("请选择已有会话序号/粘贴session_id，直接回车新建：").strip()
        if choice == "":
            session_id = uuid.uuid4().hex
            print(f"已创建新的 session_id: {session_id}")
        else:
            picked = None
            if choice.isdigit():
                idx = int(choice)
                if 0 <= idx < len(existing):
                    picked = existing[idx]
            elif choice in existing:
                picked = choice
            session_id = picked or uuid.uuid4().hex
            if picked:
                print(f"将使用已有 session_id: {session_id}")
            else:
                print(f"输入无效，已创建新的 session_id: {session_id}")
    else:
        session_id = uuid.uuid4().hex
        print(f"未发现历史会话，已创建新的 session_id: {session_id}")

    orch = Orchestrator(general_router, general_answer, domain_agents,
                        user_id=user_id, session_id=session_id)
    # restore states via SessionBase
    await orch.restore()

    # Switch to UserAgent-driven loop per AgentScope best practice
    from agentscope.agent import UserAgent
    user_agent = UserAgent(name="user")
    assistant = OrchestratorAgent(orch, name="howtolive")

    print("howtolive CLI（UserAgent 对话模式）。输入 'exit' 退出。\n")
    msg = None
    try:
        while True:
            res = await assistant(msg)
            # 方案B：仅保留智能体内部打印，这里不再重复打印文本
            msg = await user_agent(res)
            if msg.get_text_content() == "exit":
                break
    finally:
        # 清理：关闭 MCP 客户端
        if mcp_manager:
            print("\n[MCP] 正在关闭 MCP 服务...")
            await mcp_manager.close_all()
            print("[MCP] ✓ MCP 服务已关闭")


if __name__ == "__main__":
    asyncio.run(main())


