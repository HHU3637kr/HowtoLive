# AgentScope Studio 使用指南

## 📊 什么是 AgentScope Studio？

AgentScope Studio 是一个本地 Web 应用，提供：
- 🔍 **Agent 执行可视化** - 查看 Agent 思考、工具调用、响应的完整流程
- 📈 **Token 监控** - 统计每次请求的 token 消耗和成本
- 📝 **会话追踪** - 记录和回放所有 Agent 交互
- 🐛 **调试工具** - 快速定位问题和优化 prompt

---

## 🚀 快速开始

### 1. 安装 Studio

```bash
npm install -g @agentscope/studio
```

### 2. 启动 Studio

**方式1：使用脚本（推荐）**
```bash
# Windows PowerShell
.\backend\start_studio.ps1

# 或者直接运行
cd backend
.\start_studio.ps1
```

**方式2：手动启动**
```bash
# 设置端口为 5000
set PORT=5000  # Windows CMD
# 或
$env:PORT = "5000"  # PowerShell

as_studio
```

### 3. 启动后端 API

```bash
cd backend
python -m api.main
```

启动时会看到：
```
✓ AgentScope Studio 已连接: http://localhost:5000
```

### 4. 访问 Studio

浏览器打开：`http://localhost:5000`

---

## 📋 配置说明

### 配置文件：`backend/config/studio.yaml`

```yaml
studio:
  enabled: true  # 是否启用（生产环境建议关闭）
  url: "http://localhost:5000"  # Studio 地址
  port: 5000  # 端口（避开前端的 3000）
  project_name: "HowtoLive"  # 项目名称
  
  tracing:
    enabled: true  # 是否启用追踪
    save_dir: "backend/.studio_traces"  # 追踪数据目录
```

### 启用/禁用 Studio

**禁用 Studio（生产环境）：**
```yaml
studio:
  enabled: false
```

**或者直接删除/重命名配置文件。**

---

## 🎯 Studio 功能

### 1. Dashboard（仪表盘）
- 查看项目概览
- Token 使用统计
- 请求数量统计
- 成本估算

### 2. Runs（运行记录）
- 所有会话的执行记录
- 每次请求的详细信息
- 执行时间统计

### 3. Traces（追踪）
- 可视化 Agent 执行流程
- 查看每一步的输入输出
- 工具调用的参数和结果
- LLM 调用的 prompt 和响应

### 4. Friday 助手
- 内置的 AgentScope 开发助手
- 回答 AgentScope 相关问题
- 提供代码示例

---

## 📊 使用场景

### 开发调试

**查看 Agent 行为：**
1. 发送消息到 Web UI
2. 在 Studio 中查看完整执行流程
3. 检查每个 Agent 的输入输出
4. 验证工具调用是否正确

**优化 Prompt：**
1. 在 Traces 中查看 LLM 的完整 prompt
2. 分析响应质量
3. 调整 system prompt
4. 对比优化前后的效果

### 性能监控

**Token 优化：**
- 查看哪个 Agent 消耗最多 token
- 识别冗余的 LLM 调用
- 优化 context 长度

**速度优化：**
- 找出慢查询
- 优化 RAG 检索
- 减少不必要的工具调用

### 问题排查

**调试工具调用：**
- 查看工具是否被正确注册
- 检查工具参数是否正确
- 验证工具返回值

**追踪错误：**
- 查看错误发生时的完整上下文
- 回放问题会话
- 对比正常和异常的执行流程

---

## 🔧 端口说明

**项目端口分配：**
- `3000` - React 前端
- `5000` - AgentScope Studio
- `6333` - Qdrant 向量数据库
- `8000` - FastAPI 后端

**修改 Studio 端口：**

如果 5000 端口也被占用，修改 `backend/config/studio.yaml`：

```yaml
studio:
  url: "http://localhost:6000"  # 改为其他端口
  port: 6000
```

启动时使用：
```bash
$env:PORT = "6000"
as_studio
```

---

## 📝 注意事项

### 开发环境
- ✅ 启用 Studio，方便调试
- ✅ 启用 tracing，记录所有执行

### 生产环境
- ❌ 禁用 Studio（性能开销）
- ⚠️ 如需监控，使用专业的 APM 工具

### 数据隐私
- 追踪数据保存在本地 `backend/.studio_traces`
- 包含用户消息和 Agent 响应
- 生产环境需要定期清理

---

## 🎨 Studio 界面示例

访问 `http://localhost:5000` 后，你会看到：

```
┌─────────────────────────────────────────┐
│  AgentScope Studio - HowtoLive          │
├─────────────────────────────────────────┤
│  📊 Dashboard                            │
│  ├─ Total Requests: 42                  │
│  ├─ Total Tokens: 12,345               │
│  └─ Estimated Cost: $0.12              │
│                                          │
│  📝 Recent Runs                          │
│  ├─ [16:38] 用户: Rking - "红烧肉怎么做" │
│  │   └─ Route: howtocook                │
│  │   └─ Tool Calls: 1                   │
│  │   └─ Tokens: 523                     │
│  │                                       │
│  ├─ [16:29] 用户: Rking - "早餐吃什么"   │
│  │   └─ Route: howtoeat                 │
│  │   └─ Tool Calls: 2                   │
│  └─ ...                                  │
└─────────────────────────────────────────┘
```

点击任何一条记录，可以查看详细的执行流程图！

---

## 🔗 相关资源

- [AgentScope Studio 官方文档](https://doc.agentscope.io/zh_CN/tutorial/task_studio.html)
- [AgentScope 可视化教程](https://doc.agentscope.io/zh_CN/tutorial/visualization.html)

---

## ❓ 常见问题

### Q: Studio 无法连接？
**A:** 确保：
1. Studio 已启动（`as_studio`）
2. 端口正确（5000）
3. 后端启动时看到"Studio 已连接"提示

### Q: 看不到追踪数据？
**A:** 检查：
1. `studio.yaml` 中 `enabled: true`
2. `tracing.enabled: true`
3. 重启后端 API

### Q: 端口冲突？
**A:** 修改 `studio.yaml` 中的 `port` 和 `url`，然后用 `PORT=新端口 as_studio` 启动

---

## 🎯 下一步

1. ✅ 启动 Studio: `.\backend\start_studio.ps1`
2. ✅ 启动后端: `python -m backend.api.main`
3. ✅ 访问 Studio: `http://localhost:5000`
4. ✅ 发送消息，查看可视化追踪！

