# HowToLive 项目文档

欢迎来到 HowToLive 项目文档中心！这里包含了项目的完整文档。

## 📋 文档目录

### 🚀 入门指南
- [**快速开始**](./QUICK_START.md) - 5分钟快速上手指南
- [**文档维护指南**](./DOCUMENTATION_GUIDE.md) - 如何编写和维护项目文档

### 🔧 后端文档
- [**API 使用指南**](./backend/API_GUIDE.md)
  - API 端点说明
  - 请求响应格式
  - 认证机制
  - 测试方法
  
- [**架构文档**](./backend/ARCHITECTURE.md)
  - 三层资源管理架构
  - 并发安全性设计
  - 性能优化策略
  - 可扩展性分析
  
- [**RAG 知识库系统**](./backend/RAG_SYSTEM.md)
  - RAG 系统概述
  - 知识库配置
  - 使用方法
  - 故障排查

### 💻 前端文档
- [**前端使用指南**](./frontend/FRONTEND_GUIDE.md)
  - 项目结构
  - 启动步骤
  - 功能特性
  - 部署指南

### 🛠️ 工具文档
- [**Studio 使用指南**](./tools/STUDIO_GUIDE.md)
  - AgentScope Studio 介绍
  - 可视化调试
  - 性能监控
  - Token 统计

## 📖 文档使用建议

### 如果你是新用户
1. 从 [**快速开始**](./QUICK_START.md) 开始
2. 阅读 [**API 使用指南**](./backend/API_GUIDE.md) 了解接口
3. 查看 [**前端使用指南**](./frontend/FRONTEND_GUIDE.md) 使用界面

### 如果你是开发者
1. 先阅读 [**架构文档**](./backend/ARCHITECTURE.md) 理解系统设计
2. 参考 [**API 使用指南**](./backend/API_GUIDE.md) 进行开发
3. 使用 [**Studio 使用指南**](./tools/STUDIO_GUIDE.md) 进行调试

### 如果你想扩展知识库
1. 阅读 [**RAG 知识库系统**](./backend/RAG_SYSTEM.md)
2. 使用提供的工具脚本管理知识

## 🎯 文档原则

本项目文档遵循以下原则：

1. **清晰性** - 5分钟内能理解核心内容
2. **完整性** - 记录 What（是什么）和 Why（为什么）
3. **实用性** - 言之有物，提供实际示例
4. **及时性** - 与代码保持同步更新

## 🔄 文档更新

文档与代码同步更新：
- 代码变更后，相关文档会同步更新
- 重大架构调整会更新架构文档
- API 接口变更会同步更新 API 文档

## 💡 文档反馈

如发现文档问题或有改进建议：
1. 提交 Issue 说明问题
2. 或直接提交 PR 修改文档

## 📊 文档结构

```
docs/
├── README.md                    # 本文件 - 文档总览
├── QUICK_START.md              # 快速开始指南
├── DOCUMENTATION_GUIDE.md      # 文档维护指南
├── CHANGELOG.md                # 变更日志
├── backend/                    # 后端文档
│   ├── API_GUIDE.md           # API 使用指南
│   ├── ARCHITECTURE.md        # 架构文档
│   └── RAG_SYSTEM.md          # RAG 系统说明
├── frontend/                   # 前端文档
│   └── FRONTEND_GUIDE.md      # 前端使用指南
└── tools/                      # 工具文档
    └── STUDIO_GUIDE.md        # Studio 使用指南
```

## 🌟 开始探索

选择一个文档开始你的 HowToLive 之旅吧！

建议从 [**快速开始**](./QUICK_START.md) 开始 →

