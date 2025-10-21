"""会话管理服务

负责会话的创建、列表、删除和历史消息读取
复用现有的 .sessions/ 目录结构
"""

from __future__ import annotations

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.api.models import SessionInfo, SessionDetail, Message


class SessionService:
    """会话管理服务"""
    
    def __init__(self, sessions_base_dir: str = "backend/.sessions"):
        """初始化会话服务
        
        Args:
            sessions_base_dir: 会话存储根目录
        """
        self.sessions_base_dir = sessions_base_dir
    
    def _get_user_sessions_dir(self, user_id: str, username: str) -> Path:
        """获取用户的会话目录路径
        
        使用 {user_id}_{username} 格式，更易读且唯一
        支持向后兼容：如果旧格式目录存在则使用旧目录
        
        Args:
            user_id: 用户ID
            username: 用户名
            
        Returns:
            用户会话目录路径
        """
        # 新格式：user_id_username
        new_format_dir = Path(self.sessions_base_dir) / f"{user_id}_{username}"
        
        # 旧格式兼容：只有 user_id 或只有 username
        old_format_id_dir = Path(self.sessions_base_dir) / str(user_id)
        old_format_name_dir = Path(self.sessions_base_dir) / username
        
        # 优先使用新格式，如果不存在则检查旧格式
        if new_format_dir.exists():
            return new_format_dir
        elif old_format_id_dir.exists():
            # 找到旧格式目录，返回它（向后兼容）
            return old_format_id_dir
        elif old_format_name_dir.exists():
            # 找到更老的格式（只有用户名），返回它
            return old_format_name_dir
        else:
            # 都不存在，返回新格式路径（创建时使用）
            return new_format_dir
    
    def _get_session_dir(self, user_id: str, username: str, session_id: str) -> Path:
        """获取会话目录路径
        
        Args:
            user_id: 用户ID
            username: 用户名
            session_id: 会话ID
            
        Returns:
            会话目录路径
        """
        return self._get_user_sessions_dir(str(user_id), username) / session_id
    
    def create_session(self, user_id: str, username: str, title: Optional[str] = None) -> str:
        """创建新会话
        
        Args:
            user_id: 用户ID
            username: 用户名
            title: 会话标题（可选）
            
        Returns:
            新创建的会话ID
        """
        # 生成会话ID
        session_id = uuid.uuid4().hex
        
        # 创建会话目录
        session_dir = self._get_session_dir(str(user_id), username, session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建会话元信息文件
        meta = {
            "session_id": session_id,
            "title": title or f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        with open(session_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        return session_id
    
    def list_sessions(self, user_id: str, username: str) -> list[SessionInfo]:
        """列出用户的所有会话
        
        Args:
            user_id: 用户ID
            username: 用户名
            
        Returns:
            会话信息列表
        """
        sessions_dir = self._get_user_sessions_dir(str(user_id), username)
        
        if not sessions_dir.exists():
            return []
        
        sessions = []
        for session_path in sessions_dir.iterdir():
            if not session_path.is_dir():
                continue
            
            session_id = session_path.name
            
            # 读取元信息
            meta_file = session_path / "meta.json"
            timeline_file = session_path / "timeline.json"
            
            # 如果是老格式（没有 meta.json），从 timeline 推断
            if not meta_file.exists() and timeline_file.exists():
                with open(timeline_file, "r", encoding="utf-8") as f:
                    timeline = json.load(f)
                
                title = f"会话 {session_id[:8]}"
                created_at = datetime.now()
                updated_at = datetime.now()
                message_count = len(timeline)
            elif meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                
                title = meta.get("title", f"会话 {session_id[:8]}")
                created_at = datetime.fromisoformat(meta["created_at"])
                updated_at = datetime.fromisoformat(meta["updated_at"])
                
                # 统计消息数量
                if timeline_file.exists():
                    with open(timeline_file, "r", encoding="utf-8") as f:
                        timeline = json.load(f)
                    message_count = len(timeline)
                else:
                    message_count = 0
            else:
                continue
            
            sessions.append(SessionInfo(
                session_id=session_id,
                title=title,
                created_at=created_at,
                updated_at=updated_at,
                message_count=message_count,
            ))
        
        # 按更新时间倒序排列
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        return sessions
    
    def get_session_detail(self, user_id: str, username: str, session_id: str) -> Optional[SessionDetail]:
        """获取会话详情（包含历史消息）
        
        Args:
            user_id: 用户ID
            username: 用户名
            session_id: 会话ID
            
        Returns:
            会话详情，如果不存在则返回 None
        """
        session_dir = self._get_session_dir(str(user_id), username, session_id)
        
        if not session_dir.exists():
            return None
        
        # 读取元信息
        meta_file = session_dir / "meta.json"
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            title = meta.get("title", f"会话 {session_id[:8]}")
            created_at = datetime.fromisoformat(meta["created_at"])
            updated_at = datetime.fromisoformat(meta["updated_at"])
        else:
            title = f"会话 {session_id[:8]}"
            created_at = datetime.now()
            updated_at = datetime.now()
        
        # 读取历史消息
        messages = self.get_session_messages(user_id, username, session_id)
        
        return SessionDetail(
            session_id=session_id,
            title=title,
            created_at=created_at,
            updated_at=updated_at,
            messages=messages,
        )
    
    def get_session_messages(self, user_id: str, username: str, session_id: str) -> list[Message]:
        """获取会话的历史消息
        
        Args:
            user_id: 用户ID
            username: 用户名
            session_id: 会话ID
            
        Returns:
            消息列表
        """
        session_dir = self._get_session_dir(str(user_id), username, session_id)
        timeline_file = session_dir / "timeline.json"
        
        if not timeline_file.exists():
            return []
        
        with open(timeline_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 提取 timeline 数组（如果是新格式）
        if isinstance(data, dict) and "timeline" in data:
            timeline = data["timeline"]
        elif isinstance(data, list):
            timeline = data
        else:
            return []
        
        # 转换为 Message 对象
        messages = []
        for msg in timeline:
            try:
                # 安全解析时间戳
                timestamp = None
                if msg.get("timestamp"):
                    try:
                        timestamp = datetime.fromisoformat(msg["timestamp"])
                    except (ValueError, TypeError):
                        timestamp = None
                
                # 安全提取内容
                content = msg.get("content", "")
                if not isinstance(content, str):
                    content = str(content)
                
                # 使用 agent 或 name 字段作为 role
                role = msg.get("agent") or msg.get("name", "unknown")
                
                # 使用 text 或 content 字段
                if not content:
                    content = msg.get("text", "")
                    if not isinstance(content, str):
                        content = str(content)
                
                messages.append(Message(
                    role=role,
                    content=content,
                    timestamp=timestamp,
                ))
            except Exception as e:
                # 跳过解析失败的消息
                print(f"解析消息失败: {e}, 消息: {msg}")
                continue
        
        return messages
    
    def delete_session(self, user_id: str, username: str, session_id: str) -> bool:
        """删除会话
        
        Args:
            user_id: 用户ID
            username: 用户名
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        session_dir = self._get_session_dir(str(user_id), username, session_id)
        
        if not session_dir.exists():
            return False
        
        # 删除会话目录
        import shutil
        shutil.rmtree(session_dir)
        
        return True

