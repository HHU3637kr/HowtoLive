"""Pydantic 数据模型

定义 API 请求和响应的数据结构
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============ 用户认证相关 ============

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    email: Optional[str] = Field(None, description="邮箱（可选）")


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    """用户信息"""
    id: int
    username: str
    email: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Pydantic v2 配置


# ============ 会话相关 ============

class SessionCreate(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field(None, description="会话标题（可选）")


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class Message(BaseModel):
    """聊天消息"""
    role: str  # "user" 或 agent 名称
    content: str
    timestamp: Optional[datetime] = None


class SessionDetail(BaseModel):
    """会话详情（包含消息历史）"""
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[Message]


# ============ 聊天相关 ============

class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户消息")


class ChatResponse(BaseModel):
    """聊天响应（非流式）"""
    message_id: str
    role: str
    content: str
    timestamp: datetime


# ============ SSE 流式响应 ============

class StreamChunk(BaseModel):
    """流式响应数据块"""
    type: str  # "start", "token", "done", "error"
    content: Optional[str] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    error: Optional[str] = None

