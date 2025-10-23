# 变更日志 (Changelog)

本文档记录 HowToLive 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## 版本说明

- **Major (主版本号)**：不兼容的 API 变更
- **Minor (次版本号)**：向下兼容的功能新增
- **Patch (修订号)**：向下兼容的问题修正

---

## [未发布]

### 新增
- 无

### 变更
- 无

### 修复
- 无

### 移除
- 无

---

## [1.0.0] - 2025-10-23

### 项目初始版本

#### 新增

**核心功能：**
- ✅ 多 Agent 智能对话系统
  - howtoeat - 饮食营养 Agent
  - howtocook - 烹饪方法 Agent
  - howtosleep - 睡眠改善 Agent
  - howtoexercise - 运动训练 Agent
- ✅ 智能路由系统，自动分发用户请求到合适的 Agent
- ✅ 长期记忆系统（mem0），记住用户偏好和个性化信息
- ✅ RAG 知识库系统，支持全局和用户个人知识库
- ✅ MCP 工具集成，扩展 Agent 能力

**后端架构：**
- ✅ FastAPI Web API 服务
- ✅ 三层资源管理架构（全局资源、用户资源、请求资源）
- ✅ 异步并发支持，支持多用户多会话
- ✅ JWT 认证系统
- ✅ 会话管理系统
- ✅ SSE 流式响应

**前端界面：**
- ✅ React + TypeScript 前端应用
- ✅ ChatGPT 风格的对话界面
- ✅ 会话管理（创建、切换、删除）
- ✅ 实时流式显示 AI 回复
- ✅ Zustand 状态管理
- ✅ Tailwind CSS 响应式设计

**开发工具：**
- ✅ AgentScope Studio 集成（可视化调试）
- ✅ 知识库管理工具脚本
- ✅ Qdrant 向量数据库集成

**文档系统：**
- ✅ 完整的项目文档
  - 项目 README
  - 快速开始指南
  - API 使用指南
  - 架构文档
  - RAG 系统说明
  - 前端使用指南
  - Studio 使用指南
- ✅ 文档维护指南
- ✅ 变更日志（本文件）

#### 技术栈

**后端：**
- Python 3.10+
- FastAPI
- AgentScope
- Qwen (通义千问)
- Qdrant (向量数据库)
- mem0 (长期记忆)
- SQLite (用户数据)

**前端：**
- React 18
- TypeScript
- Tailwind CSS
- Zustand
- Axios

**开发工具：**
- Docker (Qdrant)
- AgentScope Studio
- Conda (环境管理)

---

## 版本对照表

| 版本 | 发布日期 | 主要变更 |
|------|---------|---------|
| 1.0.0 | 2025-10-23 | 项目初始发布 |

---

## 如何添加变更记录

当你对项目进行重要变更时，请按以下步骤更新本文件：

### 1. 确定变更类型

- **新增 (Added)**: 新功能
- **变更 (Changed)**: 现有功能的变化
- **弃用 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: Bug 修复
- **安全 (Security)**: 安全相关的变更

### 2. 确定版本号变更

根据 [语义化版本](https://semver.org/lang/zh-CN/)：

- **MAJOR (X.0.0)**: 不兼容的 API 变更
  - 例如：删除或重命名 API 端点
  - 例如：修改响应格式导致不兼容
  
- **MINOR (1.X.0)**: 向下兼容的功能新增
  - 例如：添加新的 API 端点
  - 例如：添加新的 Agent
  
- **PATCH (1.0.X)**: 向下兼容的问题修正
  - 例如：Bug 修复
  - 例如：性能优化

### 3. 添加记录

在 `[未发布]` 部分下添加你的变更：

```markdown
## [未发布]

### 新增
- 添加了用户头像上传功能 (#123)
- 新增 Agent: howtowork (工作效率助手)

### 变更
- 优化了 RAG 检索速度，提升 50% (#456)

### 修复
- 修复了会话切换时消息丢失的问题 (#789)
```

### 4. 发布版本时

当准备发布新版本时：

1. 将 `[未发布]` 改为版本号和日期
2. 创建新的 `[未发布]` 部分
3. 更新版本对照表
4. 提交代码时打上 git tag

**示例：**

```markdown
## [未发布]

### 新增
- 无

### 变更
- 无

---

## [1.1.0] - 2025-11-01

### 新增
- 添加了用户头像上传功能
```

## 相关链接

- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) - 变更日志标准
- [语义化版本](https://semver.org/lang/zh-CN/) - 版本号规范
- [项目 README](../README.md) - 项目概览
- [文档维护指南](./DOCUMENTATION_GUIDE.md) - 文档规范

---

**记住：及时更新变更日志，让用户和开发者了解项目的演进！** 📝

