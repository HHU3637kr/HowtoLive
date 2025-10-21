"""聊天路由

提供 SSE 流式聊天接口
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from backend.api.models import User, ChatRequest
from backend.api.services.chat_service import ChatService
from backend.api.middleware.auth import get_current_user


router = APIRouter(prefix="/api/chat", tags=["聊天"])


def get_chat_service() -> ChatService:
    """获取聊天服务实例（依赖注入）"""
    from backend.api.main import chat_service
    return chat_service


@router.post("/stream", summary="流式聊天（SSE）")
async def chat_stream(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """流式聊天接口（使用 Server-Sent Events）
    
    Args:
        chat_request: 聊天请求（包含 session_id 和 message）
        current_user: 当前登录用户
        chat_service: 聊天服务实例
        
    Returns:
        SSE 事件流
        
    事件格式：
        data: {"type": "start", "session_id": "xxx"}
        data: {"type": "token", "content": "字"}
        data: {"type": "done", "message_id": "xxx"}
        data: {"type": "error", "error": "错误信息"}
    """
    # 创建 SSE 事件生成器
    async def event_generator():
        async for chunk in chat_service.stream_chat(
            user_id=str(current_user.id),
            username=current_user.username,
            session_id=chat_request.session_id,
            message=chat_request.message,
        ):
            yield chunk
    
    return EventSourceResponse(event_generator())

