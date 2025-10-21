"""用户认证路由

提供注册、登录、用户信息等 API
"""

from __future__ import annotations

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.models import UserRegister, UserLogin, Token, User
from backend.api.services.auth_service import AuthService
from backend.api.middleware.auth import get_auth_service, get_current_user


router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=User, summary="用户注册")
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
):
    """注册新用户
    
    Args:
        user_data: 用户注册信息
        
    Returns:
        创建的用户信息
        
    Raises:
        HTTPException: 如果用户名已存在
    """
    user_id = auth_service.register_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
    )
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 获取创建的用户信息
    user = auth_service.get_user_by_id(user_id)
    return user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """用户登录，返回 JWT token
    
    Args:
        user_data: 登录信息
        
    Returns:
        JWT token
        
    Raises:
        HTTPException: 如果用户名或密码错误
    """
    user = auth_service.authenticate_user(
        username=user_data.username,
        password=user_data.password,
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建 JWT token
    access_token_expires = timedelta(minutes=1440)  # 24小时
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username},  # sub 必须是字符串
        expires_delta=access_token_expires,
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """获取当前登录用户的信息
    
    需要认证
    
    Returns:
        当前用户信息
    """
    return current_user


@router.post("/logout", summary="退出登录")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """退出登录
    
    注意：JWT 是无状态的，实际上只需要前端删除 token 即可
    这个端点主要用于记录日志或执行其他清理操作
    
    Returns:
        成功消息
    """
    return {"message": "退出登录成功"}

