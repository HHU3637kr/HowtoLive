"""会话管理路由

提供会话的创建、列表、查看、删除等 API
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.models import User, SessionCreate, SessionInfo, SessionDetail
from backend.api.services.session_service import SessionService
from backend.api.middleware.auth import get_current_user


router = APIRouter(prefix="/api/sessions", tags=["会话管理"])


def get_session_service() -> SessionService:
    """获取会话服务实例（依赖注入）"""
    from backend.api.main import session_service
    return session_service


@router.get("", response_model=List[SessionInfo], summary="获取会话列表")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    """获取当前用户的所有会话列表
    
    Returns:
        会话信息列表，按更新时间倒序排列
    """
    sessions = session_service.list_sessions(current_user.id, current_user.username)
    return sessions


@router.post("", response_model=SessionInfo, summary="创建新会话")
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    """创建新会话
    
    Args:
        session_data: 会话创建数据
        
    Returns:
        新创建的会话信息
    """
    session_id = session_service.create_session(
        user_id=current_user.id,
        username=current_user.username,
        title=session_data.title,
    )
    
    # 获取创建的会话详情
    sessions = session_service.list_sessions(current_user.id, current_user.username)
    created_session = next((s for s in sessions if s.session_id == session_id), None)
    
    if created_session is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="会话创建失败",
        )
    
    return created_session


@router.get("/{session_id}", response_model=SessionDetail, summary="获取会话详情")
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    """获取会话详情（包含历史消息）
    
    Args:
        session_id: 会话ID
        
    Returns:
        会话详情
        
    Raises:
        HTTPException: 如果会话不存在
    """
    session_detail = session_service.get_session_detail(current_user.id, current_user.username, session_id)
    
    if session_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )
    
    return session_detail


@router.delete("/{session_id}", summary="删除会话")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    """删除指定会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        成功消息
        
    Raises:
        HTTPException: 如果会话不存在
    """
    success = session_service.delete_session(current_user.id, current_user.username, session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )
    
    return {"message": "会话已删除"}

