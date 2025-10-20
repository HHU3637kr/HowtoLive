"""MCP 客户端管理器

负责：
1. 根据配置创建不同协议的 MCP 客户端（StdIO / HTTP）
2. 管理客户端的连接/关闭生命周期
3. 自动注册工具并创建工具组
4. 提供简洁的接口给外部使用
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentscope.tool import Toolkit

if TYPE_CHECKING:
    from .config import MCPConfig, MCPServerConfig


class MCPManager:
    """MCP 客户端管理器"""
    
    def __init__(self, mcp_config: MCPConfig):
        """初始化 MCP 管理器
        
        Args:
            mcp_config: MCP 配置对象
        """
        self.config = mcp_config
        self.clients: dict[str, any] = {}  # server_name -> client
        self.toolkits: dict[str, Toolkit] = {}  # server_name -> toolkit
    
    def _create_client(self, name: str, server_cfg: MCPServerConfig):
        """根据配置创建 MCP 客户端
        
        Args:
            name: 服务器名称
            server_cfg: 服务器配置
            
        Returns:
            MCP 客户端实例（有状态）
        """
        if server_cfg.protocol == "stdio":
            # 创建 StdIO 有状态客户端
            from agentscope.mcp import StdIOStatefulClient
            
            return StdIOStatefulClient(
                name=name,
                command=server_cfg.command,
                args=server_cfg.args or [],
            )
        
        elif server_cfg.protocol == "http":
            # 创建 HTTP 有状态客户端
            from agentscope.mcp import HttpStatefulClient
            
            return HttpStatefulClient(
                name=name,
                transport=server_cfg.transport or "streamable_http",
                url=server_cfg.url,
            )
        
        else:
            raise ValueError(f"不支持的 MCP 协议: {server_cfg.protocol}")
    
    async def initialize(self) -> None:
        """初始化所有启用的 MCP 服务
        
        执行步骤：
        1. 创建客户端
        2. 连接服务器
        3. 创建 Toolkit 和工具组
        4. 注册 MCP 工具
        """
        for server_name, server_cfg in self.config.servers.items():
            if not server_cfg.enabled:
                continue
            
            print(f"[MCP] 正在初始化 {server_name}...")
            
            try:
                # 1. 创建客户端
                client = self._create_client(server_name, server_cfg)
                
                # 2. 连接服务器（有状态客户端需要显式连接）
                await client.connect()
                print(f"[MCP]   ✓ 已连接到 {server_name}")
                
                # 3. 创建 Toolkit
                toolkit = Toolkit()
                
                # 4. 如果配置了工具组，先创建工具组
                group_name = None
                if server_cfg.tool_group:
                    group_name = server_cfg.tool_group.name
                    toolkit.create_tool_group(
                        group_name=group_name,
                        description=server_cfg.tool_group.description,
                        active=server_cfg.tool_group.active,
                    )
                    print(f"[MCP]   ✓ 已创建工具组: {group_name}")
                
                # 5. 注册 MCP 工具到工具组
                await toolkit.register_mcp_client(
                    client,
                    group_name=group_name,
                )
                
                # 获取注册的工具数量
                tool_count = len(toolkit.get_json_schemas())
                print(f"[MCP]   ✓ 已注册 {tool_count} 个工具")
                
                # 6. 保存
                self.clients[server_name] = client
                self.toolkits[server_name] = toolkit
                
            except Exception as e:
                print(f"[MCP]   ✗ 初始化失败: {e}")
                # 继续处理其他 MCP 服务
                continue
    
    async def close_all(self) -> None:
        """关闭所有 MCP 客户端
        
        注意：按 LIFO（后进先出）顺序关闭，避免错误
        """
        if not self.clients:
            return
        
        print("[MCP] 正在关闭所有 MCP 客户端...")
        
        # 按逆序关闭（LIFO）
        for server_name in reversed(list(self.clients.keys())):
            client = self.clients[server_name]
            try:
                await client.close()
                print(f"[MCP]   ✓ 已关闭 {server_name}")
            except Exception as e:
                print(f"[MCP]   ✗ 关闭 {server_name} 失败: {e}")
    
    def get_toolkit(self, server_name: str) -> Toolkit | None:
        """获取指定 MCP 服务的 Toolkit
        
        Args:
            server_name: MCP 服务器名称
            
        Returns:
            Toolkit 实例，如果不存在则返回 None
        """
        return self.toolkits.get(server_name)
    
    def list_servers(self) -> list[str]:
        """列出所有已初始化的 MCP 服务器名称"""
        return list(self.clients.keys())

