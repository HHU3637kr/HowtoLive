# HowToLive 快速开始指南

本指南将帮助你在 **5 分钟内**启动 HowToLive 项目。

## ✅ 前置条件

确保你已安装：
- Python 3.10+ 
- Node.js 18+
- Docker Desktop
- Git

## 🚀 启动步骤

### 步骤 1：克隆项目（30秒）

```bash
git clone <repository-url>
cd HowtoLive
```

### 步骤 2：配置环境（1分钟）

```bash
# 创建 Python 虚拟环境
conda create -n howtolive python=3.10
conda activate howtolive

# 安装后端依赖
pip install -r backend/requirements-api.txt

# 安装前端依赖
cd frontend/howtolive-chat
npm install
cd ../..
```

### 步骤 3：配置 API Key（30秒）

编辑 `backend/config/llm.yaml`，填入你的通义千问 API Key：

```yaml
llm:
  api_key: "your-dashscope-api-key"  # 填入你的 API Key
```

> 📌 **获取 API Key**: 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/) 申请

### 步骤 4：启动向量数据库（30秒）

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File backend/start_qdrant.ps1
```

**验证启动成功**：
- 浏览器访问 `http://localhost:6333/dashboard`
- 看到 Qdrant 管理界面即成功

### 步骤 5：启动后端服务（30秒）

```bash
# ⚠️ 重要：必须在项目根目录运行
# 确保当前目录是 HowtoLive/
python -m backend.api.main
```

**或者直接运行脚本**（推荐）：
```bash
python backend/api/main.py
```

**看到以下输出即成功**：
```
✓ AgentScope Studio 已连接: http://localhost:5000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

后端运行在：`http://localhost:8000`

### 步骤 6：启动前端（30秒）

**打开新终端**：

```bash
cd frontend/howtolive-chat
npm start
```

**浏览器自动打开**：`http://localhost:3001`

## 🎉 开始使用

### 1. 注册账号
- 点击"立即注册"
- 输入用户名、密码（邮箱可选）
- 点击"注册"

### 2. 登录
- 使用刚才注册的账号登录

### 3. 创建对话
- 点击左侧"新建对话"按钮
- 或使用默认创建的会话

### 4. 开始聊天
尝试以下问题：
- "我早餐应该吃什么？" → 触发 `howtoeat` Agent
- "红烧肉怎么做？" → 触发 `howtocook` Agent
- "如何改善睡眠质量？" → 触发 `howtosleep` Agent
- "有什么适合新手的运动？" → 触发 `howtoexercise` Agent

## 🔍 验证安装

### 检查后端
访问 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 检查前端
- 界面正常显示
- 能注册、登录
- 能发送消息并收到回复

### 检查 Qdrant
访问 `http://localhost:6333/dashboard`，查看 collections 列表

## 🐛 常见问题

### Q1: 后端启动失败？
**A**: 检查：
1. 是否激活了虚拟环境：`conda activate howtolive`
2. 是否安装了依赖：`pip install -r backend/requirements-api.txt`
3. API Key 是否配置正确

### Q2: Qdrant 连接失败？
**A**: 检查：
1. Docker Desktop 是否运行
2. 执行 `docker ps | findstr qdrant` 查看容器状态
3. 重新启动：`.\backend\start_qdrant.ps1`

### Q3: 前端无法连接后端？
**A**: 检查：
1. 后端是否在 `http://localhost:8000` 运行
2. 前端是否在 `http://localhost:3001` 运行
3. 浏览器控制台是否有 CORS 错误
4. `frontend/howtolive-chat/src/config.ts` 中的 API 地址是否正确

### Q4: AI 没有回复？
**A**: 检查：
1. API Key 是否有效
2. 后端日志是否有错误信息
3. 网络是否能访问通义千问服务

## 📚 下一步

- [**查看完整 API 文档**](./backend/API_GUIDE.md) - 了解所有 API 端点
- [**阅读架构文档**](./backend/ARCHITECTURE.md) - 理解系统设计
- [**使用 Studio 调试**](./tools/STUDIO_GUIDE.md) - 可视化 Agent 执行

## 🛠️ 可选：导入知识库

为了获得更好的回答质量，可以导入领域知识：

```bash
# ⚠️ 确保在项目根目录运行
# 导入饮食知识
python -m backend.tools.import_knowledge howtoeat ./data/nutrition.txt text

# 导入烹饪菜谱
python -m backend.tools.import_knowledge howtocook ./data/recipes.pdf pdf

# 查看知识库
python -m backend.tools.list_knowledge howtoeat
```

## 🎯 系统端口说明

| 服务 | 端口 | 用途 |
|------|------|------|
| AgentScope Studio | 3000 | Agent 可视化 |
| 前端 | 3001 | React 应用 |
| Qdrant | 6333 | 向量数据库 |
| 后端 API | 8000 | FastAPI 服务 |

## 📞 需要帮助？

- 📖 [查看完整文档](./README.md)
- 🐛 [提交 Issue](https://github.com/your-repo/issues)
- 💬 [讨论区](https://github.com/your-repo/discussions)

---

**恭喜！你已成功启动 HowToLive 项目！** 🎉

现在开始与 AI 健康助手对话，开启你的健康生活之旅吧！

