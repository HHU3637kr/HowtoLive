# Multi-Agent RAG 知识库系统

## 系统概述

为每个 Agent（howtoeat, howtocook, howtosleep, howtoexercise）构建了独立的多模态 RAG 知识库系统，支持全局知识库和用户个人知识库的混合模式。

### 系统架构

```
每个 Agent 拥有两个独立的知识库：
├── 全局知识库（所有用户共享）
│   └── 存储领域专业知识（菜谱、运动方法等）
└── 用户个人知识库（每个用户独立）
    └── 存储用户的笔记、经验、上传内容
```

### 与现有系统的关系

- **RAG**：存储领域知识、方法、菜谱等结构化内容
- **mem0**：存储用户偏好、过敏信息等个性化属性
- **MCP**：提供外部数据源（如 howtocook-mcp）

## 配置文件

### `backend/config/rag.yaml`

主配置文件，包含：
- 嵌入模型配置（文本和多模态）
- 各 Agent 的知识库配置
- 向量数据库配置
- Reader 配置

```yaml
rag:
  enabled: true  # 启用/禁用 RAG 系统
  embedding:
    provider: "qwen"
    model_name: "text-embedding-v3"
    dimensions: 1024
  # ... 更多配置
```

## 使用方法

### 启动程序

程序会自动初始化 RAG 系统：

```bash
python -m backend.main
```

输出示例：
```
[RAG] 初始化 RAG 系统...
[RAG]   ✓ 文本嵌入模型已创建: text-embedding-v3
[RAG]   ✓ 多模态嵌入模型已创建: multimodal-embedding-v1
[RAG]   ✓ howtoeat 全局知识库已创建
[RAG]   ✓ howtocook 全局知识库已创建
[RAG]   ✓ howtosleep 全局知识库已创建
[RAG]   ✓ howtoexercise 全局知识库已创建
[RAG] ✓ RAG 系统初始化完成
```

### 知识库管理工具

#### 1. 导入知识到全局知识库

```bash
# 导入文本文件
python -m backend.tools.import_knowledge howtoeat ./data/nutrition.txt text

# 导入 PDF 文件
python -m backend.tools.import_knowledge howtocook ./data/recipes.pdf pdf

# 导入图片文件
python -m backend.tools.import_knowledge howtosleep ./data/sleep_tips.png image
```

#### 2. 查看知识库内容

```bash
# 查看全局知识库
python -m backend.tools.list_knowledge howtoeat

# 查看用户知识库
python -m backend.tools.list_knowledge howtocook --user Rking
```

#### 3. 清空知识库

```bash
# 清空全局知识库
python -m backend.tools.clear_knowledge howtoeat

# 清空用户知识库
python -m backend.tools.clear_knowledge howtocook --user Rking
```

## Agent 使用知识库

每个 Agent 都自动拥有两个知识库工具：

### 1. `search_knowledge(query, top_k=5)`

搜索知识库中的相关信息。

**使用场景**：
- 用户询问专业知识、方法、技巧时
- Agent 需要权威信息来回答问题时

**示例**：
```python
# Agent 内部调用
results = await search_knowledge("糖尿病饮食指南", top_k=5)
```

### 2. `add_knowledge(documents)`

将重要信息添加到用户的个人知识库。

**使用场景**：
- 用户分享有价值的经验、笔记
- 用户上传图片（如餐单照片、运动姿势图片）

**示例**：
```python
# Agent 内部调用
await add_knowledge(documents)
```

## 技术特性

1. **混合检索**：每次查询同时搜索全局知识库和用户个人知识库，合并结果
2. **多模态支持**：使用 DashScopeMultiModalEmbedding 支持图片、视频等
3. **持久化存储**：Qdrant 使用本地磁盘存储，程序重启后数据不丢失
4. **工具注册**：作为 ReActAgent 的工具，由 Agent 自主决定何时调用
5. **用户隔离**：每个用户有独立的个人知识库，但共享全局知识库

## 数据存储位置

### Qdrant 向量数据库（Docker）

所有向量数据存储在 Docker Qdrant 服务中：
- **访问地址**：`http://localhost:6333`
- **管理界面**：`http://localhost:6333/dashboard`
- **数据持久化**：Docker volume `qdrant_storage`

### Collections 列表

RAG 系统和 mem0 共用同一个 Qdrant 实例，创建以下 collections：

**RAG 知识库：**
```
- global_kb_howtoeat           # 饮食营养全局知识库
- global_kb_howtocook          # 烹饪方法全局知识库
- global_kb_howtosleep         # 睡眠改善全局知识库
- global_kb_howtoexercise      # 运动训练全局知识库
- user_kb_{user_id}_howtoeat   # 用户饮食个人知识库
- user_kb_{user_id}_howtocook  # 用户烹饪个人知识库
- user_kb_{user_id}_howtosleep # 用户睡眠个人知识库
- user_kb_{user_id}_howtoexercise # 用户运动个人知识库
```

**mem0 长期记忆：**
```
- mem0_{user_id}               # 用户的 mem0 记忆（偏好、过敏等）
```

### 启动 Qdrant 服务

**⚠️ 重要**：在使用 RAG 系统前，需要先启动 Qdrant 服务：

```powershell
# 启动 Qdrant
powershell -ExecutionPolicy Bypass -File backend/start_qdrant.ps1

# 停止 Qdrant
powershell -ExecutionPolicy Bypass -File backend/stop_qdrant.ps1

# 检查 Qdrant 状态
docker ps | findstr qdrant
```

### 查看 Qdrant 数据

访问 Qdrant 管理界面：`http://localhost:6333/dashboard`

可以查看：
- 所有 collections
- 向量数量
- 内存使用情况
- 执行搜索测试

## 后续扩展

1. **知识库管理 Web UI**（Flask/FastAPI）
   - 可视化知识库内容
   - 批量导入功能
   - 知识库统计和分析

2. **支持批量导入**（CSV、Excel）
   - 从结构化数据导入知识
   - 自动分块和向量化

3. **知识库版本管理和回滚**
   - 追踪知识库变更
   - 支持回滚到历史版本

4. **知识库统计和可视化**
   - 知识库大小统计
   - 使用频率分析
   - 知识分布可视化

## 故障排查

### Qdrant 服务未启动

**错误信息**：`Connection refused` 或 `Cannot connect to Qdrant`

**解决方法**：
```powershell
# 启动 Qdrant 服务
powershell -ExecutionPolicy Bypass -File backend/start_qdrant.ps1

# 验证服务是否运行
docker ps | findstr qdrant
```

### RAG 系统未启动

检查 `backend/config/rag.yaml` 中 `enabled` 是否为 `true`。

### 嵌入模型连接失败

**错误信息**：API 调用失败

**解决方法**：
确保环境变量 `DASHSCOPE_API_KEY` 已正确设置：
```powershell
$env:DASHSCOPE_API_KEY = "your-api-key"
```

### 向量数据库连接错误

**错误信息**：`Qdrant connection error`

**解决方法**：
1. 检查 Qdrant 服务是否运行：`docker ps | findstr qdrant`
2. 检查配置中的 `location` 是否为 `http://localhost:6333`
3. 尝试重启 Qdrant 服务

### 知识库为空

使用 `backend/tools/import_knowledge.py` 导入初始知识：
```bash
python -m backend.tools.import_knowledge howtoeat ./data/nutrition.txt text
```

