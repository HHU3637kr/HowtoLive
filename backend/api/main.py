"""FastAPI 主应用

Web 聊天界面的后端 API 服务
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.services.auth_service import AuthService
from backend.api.services.session_service import SessionService
from backend.api.services.chat_service import ChatService
from backend.api.routers import auth, sessions, chat


# 全局服务实例（用于依赖注入）
auth_service: AuthService = None
session_service: SessionService = None
chat_service: ChatService = None

# 全局资源（应用启动时初始化一次）
global_mcp_manager = None
global_rag_manager = None
global_config = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理
    
    启动时初始化服务和全局资源，关闭时清理
    """
    import time
    _total_start = time.time()
    
    global auth_service, session_service, chat_service
    global global_mcp_manager, global_rag_manager, global_config
    
    # 配置日志系统（在最开始配置）
    import logging
    import sys
    from pathlib import Path
    
    _stage_start = time.time()
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # 输出到控制台
        ]
    )
    
    # 设置特定模块的日志级别
    logging.getLogger('backend.api.services.orchestrator_adapter').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)  # 减少访问日志
    
    print(f"⏱️  [日志配置]: {time.time() - _stage_start:.2f}秒")
    
    print("=" * 80)
    print("HowToLive Web API 启动中...")
    print("=" * 80)
    
    _stage_start = time.time()
    
    # 加载配置
    from backend.src.config import load_app_config
    from backend.src.mcp_manager import MCPManager
    from backend.src.rag_manager import RAGManager
    print(f"⏱️  [导入核心模块]: {time.time() - _stage_start:.2f}秒")
    
    # 获取配置目录路径
    _current_dir = Path(__file__).parent
    _backend_dir = _current_dir.parent
    
    _stage_start = time.time()
    
    # 初始化 AgentScope Studio（如果启用）
    import agentscope
    print(f"⏱️  [导入 AgentScope]: {time.time() - _stage_start:.2f}秒")
    _stage_start = time.time()
    
    studio_config_path = _backend_dir / "config" / "studio.yaml"
    if studio_config_path.exists():
        import yaml
        with open(studio_config_path, "r", encoding="utf-8") as f:
            studio_cfg = yaml.safe_load(f).get("studio", {})
        
        if studio_cfg.get("enabled", False):
            try:
                # 正确的 agentscope.init 参数
                agentscope.init(
                    studio_url=studio_cfg.get("url", "http://localhost:3000"),
                    project=studio_cfg.get("project_name", "HowtoLive"),
                )
                print(f"✓ AgentScope Studio 已连接: {studio_cfg['url']}")
            except Exception as e:
                print(f"⚠️ AgentScope Studio 连接失败: {e}")
                print(f"   提示: 请先启动 Studio (端口 {studio_cfg.get('port', 3000)})")
    
    print(f"⏱️  [AgentScope Studio 初始化]: {time.time() - _stage_start:.2f}秒")
    _stage_start = time.time()
    
    # 原有配置加载
    
    # 配置文件路径：相对于 backend 目录
    config_dir = _backend_dir / "config"
    cfg = load_app_config(str(config_dir))
    global_config = cfg  # 保存全局配置
    
    # 加载 API 配置
    import yaml
    # 使用绝对路径，从项目根目录开始
    api_config_path = _backend_dir / "config" / "api.yaml"
    with open(api_config_path, "r", encoding="utf-8") as f:
        api_cfg = yaml.safe_load(f).get("api", {})
    
    print(f"⏱️  [加载配置文件]: {time.time() - _stage_start:.2f}秒")
    _stage_start = time.time()
    
    # === 第1步：初始化全局资源（耗时，但只需一次）===
    print("\n[1] 初始化全局资源...")
    
    # 初始化 MCP 管理器（全局共享）
    if cfg.mcp and cfg.mcp.servers:
        try:
            print("  [MCP] 初始化 MCP 服务...")
            global_mcp_manager = MCPManager(cfg.mcp)
            await global_mcp_manager.initialize()
            print("  ✓ MCP 管理器已初始化（全局）")
        except Exception as e:
            print(f"  ✗ MCP 初始化失败: {e}")
            global_mcp_manager = None
    
    print(f"⏱️  [MCP 初始化]: {time.time() - _stage_start:.2f}秒")
    _stage_start = time.time()
    
    # 初始化 RAG 管理器（全局共享）
    if cfg.rag and cfg.rag.enabled:
        try:
            print("  [RAG] 初始化 RAG 系统...")
            global_rag_manager = RAGManager(cfg.rag)
            await global_rag_manager.initialize()
            print("  ✓ RAG 管理器已初始化（全局）")
        except Exception as e:
            print(f"  ✗ RAG 初始化失败: {e}")
            global_rag_manager = None
    
    print(f"⏱️  [RAG 初始化]: {time.time() - _stage_start:.2f}秒")
    _stage_start = time.time()
    
    # === 第2步：初始化应用服务 ===
    print("\n[2] 初始化应用服务...")
    
    # 认证服务 - 使用绝对路径确保数据位置固定
    db_relative_path = api_cfg.get("database", {}).get("path", "data/users.db")
    db_path = _backend_dir / db_relative_path
    
    # 确保数据目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    auth_service = AuthService(
        db_path=str(db_path),
        secret_key=api_cfg.get("auth", {}).get("secret_key", "default-secret-key"),
        algorithm=api_cfg.get("auth", {}).get("algorithm", "HS256"),
    )
    print(f"  ✓ 认证服务已初始化 (数据库: {db_path})")
    
    # 会话服务 - 使用绝对路径
    sessions_relative_path = api_cfg.get("sessions", {}).get("path", ".sessions")
    sessions_dir = _backend_dir / sessions_relative_path
    session_service = SessionService(sessions_base_dir=str(sessions_dir))
    print(f"  ✓ 会话服务已初始化 (会话目录: {sessions_dir})")
    
    # 聊天服务（传入全局资源）
    chat_service = ChatService(
        global_config=global_config,
        global_mcp_manager=global_mcp_manager,
        global_rag_manager=global_rag_manager,
    )
    print("  ✓ 聊天服务已初始化")
    
    print(f"⏱️  [应用服务初始化]: {time.time() - _stage_start:.2f}秒")
    
    _total_elapsed = time.time() - _total_start
    print("\n" + "=" * 80)
    print("✓ HowToLive Web API 已启动")
    print(f"  - API 文档: http://localhost:{api_cfg.get('port', 8000)}/docs")
    print(f"  - ReDoc: http://localhost:{api_cfg.get('port', 8000)}/redoc")
    print(f"\n🚀 总启动时间: {_total_elapsed:.2f}秒")
    print("=" * 80)
    
    yield
    
    # 关闭时清理
    print("\n[关闭] 清理资源...")
    
    # 清理聊天服务
    if chat_service:
        await chat_service.cleanup_all()
    
    # 关闭全局 MCP
    if global_mcp_manager:
        print("  [MCP] 关闭全局 MCP 管理器...")
        await global_mcp_manager.close_all()
    
    print("✓ 资源清理完成")


# 创建 FastAPI 应用
app = FastAPI(
    title="HowToLive API",
    description="HowToLive 聊天系统后端 API",
    version="1.0.0",
    lifespan=lifespan,
)


# 配置 CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(chat.router)


@app.get("/", tags=["系统"])
async def root():
    """根路径，返回 API 信息"""
    return {
        "name": "HowToLive API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import yaml
    
    # 加载配置（使用绝对路径）
    _current_dir = Path(__file__).parent
    _backend_dir = _current_dir.parent
    api_config_path = _backend_dir / "config" / "api.yaml"
    with open(api_config_path, "r", encoding="utf-8") as f:
        api_cfg = yaml.safe_load(f).get("api", {})
    
    # 启动服务器
    # 热重载配置：明确指定只监测代码目录，排除数据和缓存
    reload_dirs = [
        str(_backend_dir / "api"),      # API 代码
        str(_backend_dir / "src"),      # 核心源代码
        str(_backend_dir / "config"),   # 配置文件
    ]
    
    # 排除不需要监测的文件和目录
    reload_excludes = [
        # Python 缓存和编译文件
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.Python",
        
        # 测试和覆盖率
        "**/.pytest_cache/**",
        "**/.coverage",
        "**/.tox/**",
        "**/htmlcov/**",
        
        # 数据库文件
        "**/*.db",
        "**/*.db-journal",
        "**/*.sqlite",
        "**/*.sqlite3",
        
        # 数据存储目录（双重保险，虽然已在 reload_dirs 之外）
        "**/data/**",
        "**/.sessions/**",
        "**/.ltm_storage_qdrant/**",  # mem0 长期记忆存储
        "**/.studio_traces/**",         # AgentScope Studio 追踪数据
        
        # 日志文件
        "**/*.log",
        "**/*.log.*",
        
        # 临时文件和备份
        "**/*.tmp",
        "**/*.temp",
        "**/*.bak",
        "**/*.swp",
        "**/*.swo",
        "**/*~",
        
        # 构建和分发
        "**/build/**",
        "**/dist/**",
        "**/*.egg-info/**",
        
        # IDE 和编辑器配置
        "**/.vscode/**",
        "**/.idea/**",
    ]
    
    uvicorn.run(
        "backend.api.main:app",
        host=api_cfg.get("host", "0.0.0.0"),
        port=api_cfg.get("port", 8000),
        reload=api_cfg.get("reload", False),
        reload_dirs=reload_dirs if api_cfg.get("reload", True) else None,
        reload_excludes=reload_excludes if api_cfg.get("reload", True) else None,
    )

