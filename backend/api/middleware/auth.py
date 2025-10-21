"""JWT 认证中间件

提供依赖注入函数用于验证用户身份
"""

from __future__ import annotations

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.api.models import User
from backend.api.services.auth_service import AuthService


security = HTTPBearer()


def get_auth_service() -> AuthService:
    """获取认证服务实例（依赖注入）
    
    这个函数会被 FastAPI 的依赖注入系统调用
    """
    # 从应用状态中获取（在 main.py 中设置）
    from backend.api.main import auth_service
    return auth_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """获取当前登录用户（依赖注入）
    
    Args:
        credentials: HTTP Authorization Bearer token
        auth_service: 认证服务实例
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 如果 token 无效或用户不存在
    """
    token = credentials.credentials
    
    # 验证 token
    payload = auth_service.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 提取用户ID（从字符串转换为整数）
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )
    
    # 获取用户信息
    user = auth_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[User]:
    """获取当前登录用户（可选，不强制要求认证）
    
    用于某些可选认证的端点
    """
    if credentials is None:
        return None
    
    return await get_current_user(credentials, auth_service)

