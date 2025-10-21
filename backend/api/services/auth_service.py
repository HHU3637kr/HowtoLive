"""用户认证服务

负责用户注册、登录、密码验证等
"""

from __future__ import annotations

import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from backend.api.models import User


# 使用 SHA256 进行密码哈希（简单可靠，适合开发环境）
def hash_password(password: str) -> str:
    """使用 SHA256 哈希密码
    
    Args:
        password: 明文密码
        
    Returns:
        哈希密码（hex格式）
    """
    # 添加固定盐值（生产环境应使用随机盐）
    salt = "howtolive-secret-salt"
    salted = f"{salt}:{password}"
    return hashlib.sha256(salted.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        是否匹配
    """
    return hash_password(plain_password) == hashed_password


class AuthService:
    """用户认证服务"""
    
    def __init__(self, db_path: str, secret_key: str, algorithm: str = "HS256"):
        """初始化认证服务
        
        Args:
            db_path: SQLite 数据库路径
            secret_key: JWT 密钥
            algorithm: JWT 算法
        """
        self.db_path = db_path
        self.secret_key = secret_key
        self.algorithm = algorithm
        self._init_database()
    
    def _init_database(self):
        """初始化用户数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码
            
        Returns:
            是否匹配
        """
        return verify_password(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            哈希密码
        """
        return hash_password(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建 JWT token
        
        Args:
            data: 要编码的数据（通常包含 user_id 或 username）
            expires_delta: 过期时间
            
        Returns:
            JWT token 字符串
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """验证 JWT token
        
        Args:
            token: JWT token 字符串
            
        Returns:
            解码后的数据，如果验证失败则返回 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            print(f"Token 验证失败: {e}")
            return None
        except Exception as e:
            print(f"Token 验证异常: {e}")
            return None
    
    def register_user(self, username: str, password: str, email: Optional[str] = None) -> Optional[int]:
        """注册新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
            
        Returns:
            用户ID，如果用户名已存在则返回 None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.get_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            # 用户名已存在
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            User 对象，如果验证失败则返回 None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 验证密码
        if not self.verify_password(password, row["password_hash"]):
            conn.close()
            return None
        
        # 更新最后登录时间
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.utcnow(), row["id"])
        )
        conn.commit()
        
        # 构建 User 对象
        user = User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_login=datetime.utcnow(),
        )
        
        conn.close()
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """通过 ID 获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User 对象，如果不存在则返回 None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return None
        
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None,
        )

