"""聊天服务

负责处理用户消息，调用 Orchestrator，返回流式响应
"""

from __future__ import annotations

import json
import asyncio
from typing import AsyncGenerator

from agentscope.message import Msg

from backend.api.services.orchestrator_adapter import OrchestratorAdapter


class ChatService:
    """聊天服务"""
    
    def __init__(self, global_config, global_mcp_manager, global_rag_manager):
        """初始化聊天服务
        
        Args:
            global_config: 全局配置
            global_mcp_manager: 全局 MCP 管理器
            global_rag_manager: 全局 RAG 管理器
        """
        self.orchestrator_adapter = OrchestratorAdapter(
            global_config=global_config,
            global_mcp_manager=global_mcp_manager,
            global_rag_manager=global_rag_manager,
        )
    
    async def stream_chat(
        self,
        user_id: str,
        username: str,
        session_id: str,
        message: str,
    ) -> AsyncGenerator[str, None]:
        """流式聊天生成器（SSE 格式）
        
        Args:
            user_id: 用户ID
            username: 用户名
            session_id: 会话ID
            message: 用户消息
            
        Yields:
            JSON 字符串（EventSourceResponse 会自动添加 data: 前缀和换行）
        """
        # 发送开始事件
        yield json.dumps({'type': 'start', 'session_id': session_id}, ensure_ascii=False)
        
        try:
            # 调用流式处理方法（真正的流式输出）
            async for is_final, delta_content, full_content in self.orchestrator_adapter.handle_message_stream(
                user_id=str(user_id),
                username=username,
                session_id=session_id,
                message=message,
            ):
                # 发送增量内容（delta）
                if delta_content:  # 只发送非空的增量
                    yield json.dumps({
                        'type': 'token',
                        'content': delta_content,
                        'is_final': is_final
                    }, ensure_ascii=False)
            
            # 发送完成事件
            yield json.dumps({'type': 'done', 'message_id': session_id}, ensure_ascii=False)
            
        except Exception as e:
            # 发送错误事件
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            yield json.dumps({'type': 'error', 'error': error_detail}, ensure_ascii=False)
    
    async def cleanup_all(self):
        """清理所有资源"""
        await self.orchestrator_adapter.cleanup_all()

