# HowToLive Web API 使用说明

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
conda activate howtolive

# 安装 API 额外依赖
pip install -r backend/requirements-api.txt
```

### 2. 启动 Qdrant 服务

```powershell
powershell -ExecutionPolicy Bypass -File backend/start_qdrant.ps1
```

### 3. 启动 API 服务器

```bash
# ⚠️ 必须在项目根目录运行

# 方式1：使用模块方式（推荐）
python -m backend.api.main

# 方式2：直接运行脚本
python backend/api/main.py

# 方式3：使用 uvicorn
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API 端点

### 认证相关

#### POST `/api/auth/register`
注册新用户

**请求体：**
```json
{
  "username": "testuser",
  "password": "password123",
  "email": "test@example.com"  // 可选
}
```

**响应：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2025-10-21T10:00:00",
  "last_login": null
}
```

#### POST `/api/auth/login`
用户登录，获取 JWT token

**请求体：**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### GET `/api/auth/me`
获取当前用户信息

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2025-10-21T10:00:00",
  "last_login": "2025-10-21T10:05:00"
}
```

---

### 会话管理

#### GET `/api/sessions`
获取当前用户的所有会话列表

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
[
  {
    "session_id": "abc123...",
    "title": "会话 2025-10-21 10:00",
    "created_at": "2025-10-21T10:00:00",
    "updated_at": "2025-10-21T10:30:00",
    "message_count": 15
  }
]
```

#### POST `/api/sessions`
创建新会话

**请求头：**
```
Authorization: Bearer <access_token>
```

**请求体：**
```json
{
  "title": "我的新对话"  // 可选
}
```

**响应：**
```json
{
  "session_id": "def456...",
  "title": "我的新对话",
  "created_at": "2025-10-21T11:00:00",
  "updated_at": "2025-10-21T11:00:00",
  "message_count": 0
}
```

#### GET `/api/sessions/{session_id}`
获取会话详情（包含历史消息）

**响应：**
```json
{
  "session_id": "abc123...",
  "title": "我的对话",
  "created_at": "2025-10-21T10:00:00",
  "updated_at": "2025-10-21T10:30:00",
  "messages": [
    {
      "role": "user",
      "content": "你好",
      "timestamp": "2025-10-21T10:00:00"
    },
    {
      "role": "howtolive",
      "content": "你好！有什么可以帮你的吗？",
      "timestamp": "2025-10-21T10:00:05"
    }
  ]
}
```

#### DELETE `/api/sessions/{session_id}`
删除会话

**响应：**
```json
{
  "message": "会话已删除"
}
```

---

### 聊天

#### POST `/api/chat/stream`
流式聊天接口（SSE）

**请求头：**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体：**
```json
{
  "session_id": "abc123...",
  "message": "请给我一些早餐建议"
}
```

**响应（SSE 流）：**
```
data: {"type": "start", "session_id": "abc123..."}

data: {"type": "token", "content": "好"}

data: {"type": "token", "content": "的"}

data: {"type": "token", "content": "，"}

data: {"type": "done", "message_id": "msg_xxx"}
```

**事件类型：**
- `start` - 开始响应
- `token` - 内容片段（逐字返回）
- `done` - 响应完成
- `error` - 发生错误

---

## 测试 API

### 使用 curl 测试

**1. 注册用户：**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

**2. 登录获取 token：**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

**3. 创建会话：**
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "测试会话"}'
```

**4. 发送消息（SSE）：**
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session_id>", "message": "你好"}' \
  -N  # 不缓冲输出
```

---

## 与 CLI 模式的关系

### CLI 模式（保留）

```bash
# ⚠️ 必须在项目根目录运行
# 运行 CLI 模式
python -m backend.cli
```

### Web API 模式（新增）

```bash
# ⚠️ 必须在项目根目录运行
# 运行 Web API 服务器
python -m backend.api.main
# 或
python backend/api/main.py
```

### 数据共享

- ✅ **会话数据**：CLI 和 Web API 共享 `backend/.sessions/` 目录
- ✅ **mem0 记忆**：共享同一个 Qdrant 数据库
- ✅ **RAG 知识库**：共享同一个 Qdrant 数据库
- ✅ **配置文件**：共享 `backend/config/` 目录

**这意味着**：
- 在 CLI 中创建的会话，可以在 Web 界面中查看
- 在 Web 中的对话，会被 mem0 和 RAG 记录
- 两种模式可以无缝切换

---

## 故障排查

### API 启动失败

**错误**：`ModuleNotFoundError`

**解决**：确保在正确的虚拟环境中：
```bash
conda activate howtolive
```

### 数据库错误

**错误**：`sqlite3.OperationalError`

**解决**：确保 `backend/data/` 目录存在且有写入权限

### Qdrant 连接失败

**错误**：`Connection refused`

**解决**：启动 Qdrant 服务：
```bash
powershell -ExecutionPolicy Bypass -File backend/start_qdrant.ps1
```

### CORS 错误

**错误**：前端请求被阻止

**解决**：检查 `backend/config/api.yaml` 中的 CORS 配置，确保包含前端地址

---

## 下一步

完成后端 API 后，继续开发前端 React 应用。

参考 [前端使用指南](../frontend/FRONTEND_GUIDE.md) 了解前端开发和部署详情。

