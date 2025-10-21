"""Orchestrator 适配器

将现有的 CLI Orchestrator 适配为 Web API 使用
完全复用 backend/main.py 中的初始化逻辑
"""

from __future__ import annotations

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到路径
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = Path(_CURRENT_DIR).parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agentscope.tool import Toolkit

# 配置日志记录器
logger = logging.getLogger(__name__)

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


class OrchestratorAdapter:
    """Orchestrator 适配器（三层资源管理架构）
    
    层级1: 全局资源（应用启动时初始化，所有用户共享）
      - MCP Manager, RAG Manager
    
    层级2: 用户资源（按 user_id 缓存）
      - mem0 长期记忆, 用户 RAG 知识库
    
    层级3: 会话资源（每次请求创建，支持并发）
      - Agents（新创建）, Orchestrator（新创建）
    """
    
    def __init__(self, global_config, global_mcp_manager, global_rag_manager):
        """初始化适配器
        
        Args:
            global_config: 全局配置
            global_mcp_manager: 全局 MCP 管理器（已初始化）
            global_rag_manager: 全局 RAG 管理器（已初始化）
        """
        self.config = global_config
        self.global_mcp = global_mcp_manager
        self.global_rag = global_rag_manager
        
        # 用户级资源缓存（key: user_id）
        self.user_mem0_cache: dict[str, any] = {}
        self.user_rag_cache: dict[str, dict] = {}  # {user_id: {agent_name: AgentKnowledgeBase}}
    
    async def handle_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ):
        """处理用户消息（每次请求创建新的 Orchestrator）
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            message: 用户消息
            
        Returns:
            Agent 的响应
        """
        # 1. 获取或创建用户级资源（缓存的）
        user_mem0 = await self._get_or_create_user_mem0(user_id)
        user_rag = await self._get_or_create_user_rag(user_id)
        
        # 2. 创建新的 Agents（每次请求）
        domain_agents = await self._create_agents(
            user_id=user_id,
            user_mem0=user_mem0,
            user_rag=user_rag,
        )
        
        # 3. 创建新的 Orchestrator（每次请求）
        orchestrator = await self._create_orchestrator_for_session(
            user_id=user_id,
            session_id=session_id,
            domain_agents=domain_agents,
        )
        
        # 4. 处理消息
        response = await orchestrator.handle(message)
        
        return response
    
    async def handle_message_stream(
        self,
        user_id: str,
        username: str,
        session_id: str,
        message: str,
    ):
        """处理用户消息并返回流式生成器（真正的流式输出）
        
        Args:
            user_id: 用户ID
            username: 用户名
            session_id: 会话ID
            message: 用户消息
            
        Yields:
            (is_final: bool, delta_content: str, full_content: str) 元组
        """
        from agentscope.message import Msg
        from backend.src.routing_schema import RoutingChoice
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[聊天请求] 用户: {username} (ID: {user_id}), 会话: {session_id[:8]}...")
        logger.info(f"[用户消息] {message}")
        logger.info(f"{'='*80}\n")
        
        # 1. 获取或创建用户级资源
        logger.info("[步骤 1/9] 初始化用户级资源...")
        user_mem0 = await self._get_or_create_user_mem0(user_id)
        user_rag = await self._get_or_create_user_rag(user_id)
        logger.info("  ✓ 用户资源已就绪 (mem0 + RAG)")
        
        # 2. 创建新的 Agents
        logger.info("[步骤 2/9] 创建专业 Agents...")
        domain_agents = await self._create_agents(
            user_id=user_id,
            user_mem0=user_mem0,
            user_rag=user_rag,
        )
        logger.info(f"  ✓ 已创建 {len(domain_agents['domain_agents'])} 个领域 Agent + 通用 Agent")
        
        # 3. 创建新的 Orchestrator
        logger.info("[步骤 3/9] 创建 Orchestrator 并恢复会话...")
        orchestrator = await self._create_orchestrator_for_session(
            user_id=user_id,
            username=username,
            session_id=session_id,
            domain_agents=domain_agents,
        )
        logger.info("  ✓ Orchestrator 已就绪")
        
        # 4. 路由到合适的 Agent
        logger.info("[步骤 4/9] 路由决策...")
        msg_user = Msg("user", message, "user")
        router_res = await orchestrator.general_router(msg_user, structured_model=RoutingChoice)
        choice = (router_res.metadata or {}).get("your_choice", "general")
        logger.info(f"  → 路由结果: [{choice}]")
        
        # 5. 选择目标 Agent
        logger.info("[步骤 5/9] 选择目标 Agent...")
        if choice in ("general", "none"):
            target_agent = orchestrator.general_answer
            logger.info(f"  → 使用通用 Agent")
        else:
            target_agent = orchestrator.domain_agents.get(choice, orchestrator.general_answer)
            logger.info(f"  → 使用专业 Agent: {choice}")
        
        # 6. 准备 prompt（手动构建，绕过 Agent 以支持流式输出）
        logger.info("[步骤 6/9] 准备 Agent 执行...")
        
        # 获取 Agent 的系统提示和历史消息
        agent_memory = target_agent.memory if hasattr(target_agent, 'memory') else None
        agent_sys_prompt = target_agent.sys_prompt if hasattr(target_agent, 'sys_prompt') else ""
        
        # 构建消息列表
        messages = []
        if agent_sys_prompt:
            messages.append({"role": "system", "content": agent_sys_prompt})
        
        # 添加历史消息（异步获取）
        if agent_memory:
            try:
                history = await agent_memory.get_memory()
                for hist_msg in history:
                    role = getattr(hist_msg, 'role', 'user')
                    content = getattr(hist_msg, 'content', str(hist_msg))
                    messages.append({"role": role, "content": content})
            except Exception as e:
                logger.warning(f"获取历史消息失败: {e}")
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        
        # 7. 直接调用模型获取流式输出（AgentScope 正确方式）
        logger.info("[步骤 7/9] 调用 LLM 模型生成响应...")
        
        # 检查 Agent 是否有可用工具
        has_tools = hasattr(target_agent, 'get_tools') or (hasattr(target_agent, 'toolkit') and target_agent.toolkit)
        if has_tools:
            # 列出可用工具
            tools_list = []
            if hasattr(target_agent, 'toolkit') and target_agent.toolkit:
                tools_list = list(target_agent.toolkit.tools.keys())
            logger.info(f"  🔧 Agent 已装备 {len(tools_list)} 个工具")
            if tools_list:
                logger.info(f"     可用工具: {', '.join(tools_list)}")
        
        # 🔧 使用 Hooks 机制实现流式输出 + 工具调用
        logger.info("  📡 使用 hooks 捕获 Agent 流式输出...")
        
        # 创建消息队列
        import asyncio
        message_queue = asyncio.Queue()
        last_full_text = ""
        
        # 创建 streaming hook
        async def streaming_hook(self, kwargs: dict):
            """捕获 Agent 的每条消息"""
            msg = kwargs.get("msg")
            if msg:
                # 提取消息内容 - 只提取纯文本部分
                content = ""
                if hasattr(msg, 'content'):
                    raw_content = msg.content
                    
                    # 如果是字符串，直接使用
                    if isinstance(raw_content, str):
                        content = raw_content
                    # 如果是列表（结构化数据），提取 text 类型的内容
                    elif isinstance(raw_content, list):
                        text_parts = []
                        for item in raw_content:
                            if isinstance(item, dict):
                                # 只提取 type='text' 的内容
                                if item.get('type') == 'text':
                                    text_parts.append(item.get('text', ''))
                            elif isinstance(item, str):
                                text_parts.append(item)
                        content = ''.join(text_parts)
                    else:
                        content = str(raw_content)
                else:
                    content = str(msg)
                
                # 只有非空内容才发送
                if content.strip():
                    await message_queue.put({
                        "name": getattr(msg, 'name', 'agent'),
                        "role": getattr(msg, 'role', 'assistant'),
                        "content": content
                    })
        
        # 注册 hook
        hook_name = f"streaming_hook_{session_id}"
        try:
            target_agent.register_instance_hook(
                hook_type="pre_print",
                hook_name=hook_name,
                hook=streaming_hook
            )
            
            # 后台运行 Agent
            async def run_agent():
                try:
                    response = await target_agent(msg_user)
                    await message_queue.put(None)  # 结束标记
                except Exception as e:
                    logger.error(f"Agent 执行异常: {e}", exc_info=True)
                    await message_queue.put({"error": str(e)})
                    await message_queue.put(None)
            
            # 启动 Agent 任务
            agent_task = asyncio.create_task(run_agent())
            
            # 流式输出消息
            try:
                while True:
                    # 等待消息（超时30秒）
                    message_data = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                    
                    if message_data is None:  # 结束标记
                        logger.info("  ✅ Agent 执行完成")
                        break
                    
                    if isinstance(message_data, dict) and "error" in message_data:
                        logger.error(f"  ❌ Agent 错误: {message_data['error']}")
                        break
                    
                    # 提取内容
                    content = message_data.get("content", "")
                    if content:
                        # 计算真正的增量（只发送新增部分）
                        if content.startswith(last_full_text):
                            # 内容是累积的，提取新增部分
                            delta = content[len(last_full_text):]
                            last_full_text = content
                            
                            # 只发送非空的增量
                            if delta:
                                yield (False, delta, last_full_text)
                        else:
                            # 内容不是累积的（可能是新的独立消息，如工具结果）
                            # 添加换行分隔
                            if last_full_text:
                                delta = "\n" + content
                                last_full_text += delta
                            else:
                                delta = content
                                last_full_text = content
                            
                            yield (False, delta, last_full_text)
                
                # 发送最终完整内容
                if last_full_text:
                    yield (True, "", last_full_text)
                    
            except asyncio.TimeoutError:
                logger.error("  ⏱️ Agent 执行超时")
                if last_full_text:
                    yield (True, "", last_full_text)
                else:
                    yield (True, "执行超时", "执行超时")
                    
        finally:
            # 清理 hook
            try:
                target_agent.remove_instance_hook(
                    hook_type="pre_print",
                    hook_name=hook_name
                )
            except:
                pass
            
            # 取消任务（如果还在运行）
            if 'agent_task' in locals() and not agent_task.done():
                agent_task.cancel()
        
        # 8. 保存会话状态（使用最终的响应）
        logger.info("[步骤 8/9] 保存会话状态...")
        
        # 使用 {user_id}_{username} 格式与 SessionService 保持一致
        session_user_id = f"{user_id}_{username}"
        
        agents_dict = {"general-router": orchestrator.general_router, "general": orchestrator.general_answer}
        agents_dict.update(orchestrator.domain_agents)
        await orchestrator.session.save_session_state(
            session_id=session_id,
            user_id=session_user_id,
            **agents_dict
        )
        logger.info(f"  ✓ 会话状态已保存到 {session_user_id}/{session_id[:8]}.../state.json")
        
        # 9. 保存时间线事件
        logger.info("[步骤 9/9] 保存对话历史...")
        final_response = Msg(target_agent.name, last_full_text, "assistant")
        events = [
            {"role": "user", "content": message, "name": "user"},
            {"role": "assistant", "content": last_full_text, "name": target_agent.name}
        ]
        await orchestrator.session.append_events(
            session_id=session_id,
            user_id=session_user_id,
            events=events
        )
        logger.info(f"  ✓ 对话历史已保存到 timeline.json")
        logger.info(f"{'='*80}")
        logger.info(f"[完成] 响应已发送")
        logger.info(f"{'='*80}\n")
    
    async def _get_or_create_user_mem0(self, user_id: str):
        """获取或创建用户的 mem0 长期记忆（缓存）
        
        Args:
            user_id: 用户ID
            
        Returns:
            mem0 实例
        """
        if user_id not in self.user_mem0_cache:
            # 创建 mem0
            user_ltm = build_mem0_long_term_memory(
                self.config.ltm, 
                self.config.llm, 
                user_id=user_id
            )
            user_ltm = wrap_with_logging(user_ltm)
            self.user_mem0_cache[user_id] = user_ltm
        
        return self.user_mem0_cache[user_id]
    
    async def _get_or_create_user_rag(self, user_id: str) -> dict:
        """获取或创建用户的 RAG 知识库（缓存）
        
        Args:
            user_id: 用户ID
            
        Returns:
            {agent_name: AgentKnowledgeBase} 字典
        """
        if user_id not in self.user_rag_cache:
            user_rag = {}
            if self.global_rag:
                # 为每个 Agent 获取用户的知识库
                for agent_name in ["howtoeat", "howtocook", "howtosleep", "howtoexercise"]:
                    user_rag[agent_name] = self.global_rag.get_agent_kb(agent_name, user_id)
            
            self.user_rag_cache[user_id] = user_rag
        
        return self.user_rag_cache[user_id]
    
    async def _create_agents(
        self,
        user_id: str,
        user_mem0,
        user_rag: dict,
    ) -> dict:
        """创建用户的所有 Agents（每次请求创建新的）
        
        Args:
            user_id: 用户ID
            user_mem0: 用户的 mem0 实例
            user_rag: 用户的 RAG 知识库字典
            
        Returns:
            {agent_name: agent_instance} 字典
        """
        cfg = self.config
        ltm_mode = cfg.ltm.mode if (cfg.ltm and cfg.ltm.enabled) else "agent_control"
        
        # 构建通用回答 Agent
        general_answer = build_general_answer(
            cfg.llm,
            long_term_memory=user_mem0,
            ltm_mode=ltm_mode
        )
        
        # 为每个专业 Agent 创建实例
        domain_agents = {}
        for agent_name in ["howtoeat", "howtocook", "howtosleep", "howtoexercise"]:
            # 获取 Toolkit（直接使用全局，避免 groups 丢失）
            toolkit = None
            
            # 如果是 howtocook，直接使用全局 MCP 的 Toolkit
            if agent_name == "howtocook" and self.global_mcp:
                toolkit = self.global_mcp.get_toolkit("howtocook")
                # ✅ 直接使用全局 Toolkit，保留 groups 信息
                # 工具函数是无状态的，可以安全并发使用
            
            # 获取用户的 RAG 知识库
            agent_kb = user_rag.get(agent_name)
            
            # 构建 Agent
            build_func = {
                "howtoeat": build_howtoeat,
                "howtocook": build_howtocook,
                "howtosleep": build_howtosleep,
                "howtoexercise": build_howtoexercise,
            }[agent_name]
            
            agent = build_func(
                cfg.llm,
                long_term_memory=user_mem0,
                ltm_mode=ltm_mode,
                toolkit=toolkit,
                knowledge=agent_kb,
            )
            
            domain_agents[agent_name] = agent
        
        return {
            "general_answer": general_answer,
            "domain_agents": domain_agents,
        }
    
    async def _create_orchestrator_for_session(
        self,
        user_id: str,
        username: str,
        session_id: str,
        domain_agents: dict,
    ) -> Orchestrator:
        """为会话创建 Orchestrator（每次请求创建新的）
        
        Args:
            user_id: 用户ID
            username: 用户名
            session_id: 会话ID
            domain_agents: 领域 agents 字典
            
        Returns:
            Orchestrator 实例
        """
        cfg = self.config
        
        # 使用 {user_id}_{username} 格式与 SessionService 保持一致
        session_user_id = f"{user_id}_{username}"
        
        # 1. 构建路由器
        general_router = build_general_router(cfg.llm)
        
        # 2. 创建 Orchestrator（使用组合的 user_id）
        orchestrator = Orchestrator(
            general_router,
            domain_agents["general_answer"],
            domain_agents["domain_agents"],
            user_id=session_user_id,
            session_id=session_id,
        )
        
        # 3. 恢复会话状态（如果存在）
        await orchestrator.restore()
        
        return orchestrator
    
    async def cleanup_all(self):
        """清理所有用户级资源（应用关闭时调用）"""
        # 清空用户级缓存
        self.user_mem0_cache.clear()
        self.user_rag_cache.clear()
        
        print("  [Adapter] 用户资源缓存已清理")

