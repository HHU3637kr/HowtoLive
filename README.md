# HowToLive - AI 健康生活助手

一个基于多 Agent 架构的智能健康生活助手系统，帮助用户改善饮食、运动、睡眠等生活方式。

## 📖 项目简介

HowToLive 是一个完整的 Web 应用，包含：
- 🍽️ **智能饮食建议**：营养搭配、饮食计划
- 👨‍🍳 **烹饪指导**：菜谱推荐、烹饪技巧
- 💤 **睡眠改善**：睡眠分析、改善建议
- 🏃 **运动指导**：运动计划、训练方法

## 🏗️ 技术架构

- **后端**: Python + FastAPI + AgentScope
- **前端**: React + TypeScript + Tailwind CSS
- **AI模型**: 通义千问 (Qwen)
- **向量数据库**: Qdrant
- **长期记忆**: mem0
- **知识库**: RAG (Retrieval-Augmented Generation)

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- Docker (用于 Qdrant)
- Conda (推荐)

### 1. 克隆项目
```bash
git clone <repository-url>
cd HowtoLive
```

### 2. 启动后端

```bash
# 创建虚拟环境
conda create -n howtolive python=3.10
conda activate howtolive

# 安装依赖
pip install -r backend/requirements-api.txt

# 启动 Qdrant 服务
powershell -ExecutionPolicy Bypass -File backend/start_qdrant.ps1

# 配置 API Key
# 在 backend/config/llm.yaml 中配置通义千问 API Key

# 启动后端服务（必须在项目根目录运行）
python -m backend.api.main
```

后端将运行在 `http://localhost:8000`

### 3. 启动前端

```bash
# 进入前端目录
cd frontend/howtolive-chat

# 安装依赖
npm install

# 启动开发服务器
npm start
```

前端将运行在 `http://localhost:3001`

### 4. 开始使用

1. 访问 `http://localhost:3001`
2. 注册账号并登录
3. 创建对话，开始与 AI 助手交流

## 📚 完整文档

详细文档请查看 [`docs/`](./docs/) 目录：

### 快速指南
- [📖 文档总览](./docs/README.md)
- [🚀 快速开始指南](./docs/QUICK_START.md)
- [📋 变更日志](./docs/CHANGELOG.md) - 查看版本变更历史

### 后端文档
- [📡 API 使用指南](./docs/backend/API_GUIDE.md) - API 端点、请求响应格式
- [🏗️ 架构文档](./docs/backend/ARCHITECTURE.md) - 系统架构、资源管理
- [📚 RAG 知识库系统](./docs/backend/RAG_SYSTEM.md) - 知识库配置和使用

### 前端文档
- [💻 前端使用指南](./docs/frontend/FRONTEND_GUIDE.md) - 前端开发、部署

### 工具文档
- [🔍 Studio 使用指南](./docs/tools/STUDIO_GUIDE.md) - Agent 可视化调试工具

## 🌟 核心特性

### 多 Agent 协作
- **路由 Agent**：智能识别用户意图，分发到对应专业 Agent
- **专业 Agent**：howtoeat、howtocook、howtosleep、howtoexercise
- **编排器**：统一管理 Agent 交互和会话

### 记忆系统
- **mem0 长期记忆**：记住用户偏好、过敏信息等个性化属性
- **RAG 知识库**：存储专业知识和用户笔记
- **会话历史**：持久化对话记录

### 高性能架构
- **三层资源管理**：全局资源、用户资源、请求资源
- **异步并发**：支持多用户、多会话并发
- **资源复用**：优化响应时间至 1-2 秒

### 开发体验
- **AgentScope Studio**：可视化 Agent 执行流程
- **热重载**：前后端开发热更新
- **类型安全**：TypeScript 全栈类型支持

## 🛠️ 开发工具

### 知识库管理
```bash
# 必须在项目根目录运行
# 导入知识
python -m backend.tools.import_knowledge howtoeat ./data/nutrition.txt text

# 查看知识库
python -m backend.tools.list_knowledge howtoeat

# 清空知识库
python -m backend.tools.clear_knowledge howtoeat
```

### 可视化调试
```bash
# 启动 AgentScope Studio
.\backend\start_studio.ps1

# 访问 http://localhost:3000
```

## 📊 项目结构

```
HowtoLive/
├── backend/                 # 后端服务
│   ├── api/                # FastAPI 应用
│   │   ├── routers/       # API 路由
│   │   ├── services/      # 业务逻辑
│   │   └── middleware/    # 中间件
│   ├── src/                # Agent 核心代码
│   │   ├── agents/        # Agent 实现
│   │   ├── prompts/       # Prompt 模板
│   │   └── orchestrator.py # 编排器
│   ├── config/             # 配置文件
│   └── tools/              # 工具脚本
├── frontend/               # 前端应用
│   └── howtolive-chat/    # React 应用
│       ├── src/
│       │   ├── components/ # React 组件
│       │   ├── services/   # API 服务
│       │   ├── store/      # 状态管理
│       │   └── types/      # TypeScript 类型
│       └── build/          # 生产构建
├── docs/                   # 项目文档
│   ├── backend/           # 后端文档
│   ├── frontend/          # 前端文档
│   └── tools/             # 工具文档
└── README.md              # 本文件
```

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

[MIT License](LICENSE)

## 📞 联系方式

如有问题或建议，请提交 Issue。

---

**Enjoy building a healthier life with AI! 🌟**

