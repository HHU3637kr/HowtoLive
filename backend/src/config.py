from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class LLMConfig:
    provider: str
    qwen_api_key: Optional[str]
    qwen_model: Optional[str]
    temperature: float = 0.0
    max_tokens: int = 4000
    timeout: int = 30
    streaming: bool = True
    enable_search: bool = True


@dataclass
class LTMChatModelConfig:
    provider: str
    model_name: str
    api_key_env: Optional[str] = None
    stream: bool = False


@dataclass
class EmbeddingConfig:
    provider: str
    model_name: str
    api_key_env: Optional[str] = None


@dataclass
class LTMPipelinePolicy:
    record_preferences: bool = True
    record_facts: bool = True
    # Prefer per-user limits; keep session limit for backward compatibility
    max_items_per_user: int = 200
    max_items_per_user_per_domain: int = 100
    max_items_per_session: int = 50


@dataclass
class LTMConfig:
    enabled: bool = False
    provider: str = "mem0"
    mode: str = "static_control"
    on_disk: bool = False
    chat_model: Optional[LTMChatModelConfig] = None
    embedding: Optional[EmbeddingConfig] = None
    policy: LTMPipelinePolicy = field(default_factory=LTMPipelinePolicy)


@dataclass
class MCPToolGroupConfig:
    """MCP 工具组配置"""
    name: str
    description: str = ""
    active: bool = True


@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""
    enabled: bool
    protocol: str  # "stdio" 或 "http"
    # StdIO 协议参数
    command: Optional[str] = None
    args: Optional[list[str]] = None
    # HTTP 协议参数（StreamableHTTP 或 SSE）
    transport: Optional[str] = None  # "streamable_http" 或 "sse"
    url: Optional[str] = None
    # 工具组配置
    tool_group: Optional[MCPToolGroupConfig] = None


@dataclass
class MCPConfig:
    """MCP 配置"""
    servers: dict[str, MCPServerConfig] = field(default_factory=dict)


@dataclass
class AppConfig:
    llm: LLMConfig
    ltm: Optional[LTMConfig]
    mcp: Optional[MCPConfig] = None


def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_app_config(config_dir: str = "backend/config") -> AppConfig:
    llm_raw = _load_yaml(os.path.join(config_dir, "llm.yaml")).get("llm", {})
    # env 优先覆盖
    qwen_api_key = os.getenv("QWEN_API_KEY", llm_raw.get("qwen_api_key"))
    llm = LLMConfig(
        provider=llm_raw.get("provider", "qwen"),
        qwen_api_key=qwen_api_key,
        qwen_model=llm_raw.get("qwen_model"),
        temperature=float(llm_raw.get("temperature", 0.0)),
        max_tokens=int(llm_raw.get("max_tokens", 4000)),
        timeout=int(llm_raw.get("timeout", 30)),
        streaming=bool(llm_raw.get("streaming", True)),
        enable_search=bool(llm_raw.get("enable_search", True)),
    )

    ltm_yaml = _load_yaml(os.path.join(config_dir, "ltm.yaml"))
    ltm_raw = ltm_yaml.get("long_term_memory") if ltm_yaml else None

    ltm: Optional[LTMConfig] = None
    if ltm_raw:
        chat_raw = ltm_raw.get("chat_model") or {}
        emb_raw = ltm_raw.get("embedding") or {}
        policy_raw = ltm_raw.get("policy") or {}

        chat_model = LTMChatModelConfig(
            provider=chat_raw.get("provider", "qwen"),
            model_name=chat_raw.get("model_name", "qwen3-next-80b-a3b-instruct"),
            api_key_env=chat_raw.get("api_key_env"),
            stream=bool(chat_raw.get("stream", False)),
        )
        embedding = EmbeddingConfig(
            provider=emb_raw.get("provider", "qwen"),
            model_name=emb_raw.get("model_name", "text-embedding-v2"),
            api_key_env=emb_raw.get("api_key_env"),
        )
        policy = LTMPipelinePolicy(
            record_preferences=bool(policy_raw.get("record_preferences", True)),
            record_facts=bool(policy_raw.get("record_facts", True)),
            max_items_per_user=int(policy_raw.get("max_items_per_user", policy_raw.get("max_items_per_session", 200))),
            max_items_per_user_per_domain=int(policy_raw.get("max_items_per_user_per_domain", 100)),
            max_items_per_session=int(policy_raw.get("max_items_per_session", 50)),
        )
        ltm = LTMConfig(
            enabled=bool(ltm_raw.get("enabled", False)),
            provider=ltm_raw.get("provider", "mem0"),
            mode=ltm_raw.get("mode", "static_control"),
            on_disk=bool(ltm_raw.get("on_disk", False)),
            chat_model=chat_model,
            embedding=embedding,
            policy=policy,
        )

    # 加载 MCP 配置
    mcp_yaml = _load_yaml(os.path.join(config_dir, "mcp.yaml"))
    mcp_raw = mcp_yaml.get("mcp_servers") if mcp_yaml else None
    
    mcp: Optional[MCPConfig] = None
    if mcp_raw:
        servers = {}
        for server_name, server_data in mcp_raw.items():
            # 解析工具组配置
            tool_group = None
            if server_data.get("tool_group"):
                tg_raw = server_data["tool_group"]
                tool_group = MCPToolGroupConfig(
                    name=tg_raw.get("name", f"{server_name}_tools"),
                    description=tg_raw.get("description", ""),
                    active=bool(tg_raw.get("active", True)),
                )
            
            # 创建服务器配置
            servers[server_name] = MCPServerConfig(
                enabled=bool(server_data.get("enabled", False)),
                protocol=server_data.get("protocol", "stdio"),
                command=server_data.get("command"),
                args=server_data.get("args", []),
                transport=server_data.get("transport"),
                url=server_data.get("url"),
                tool_group=tool_group,
            )
        
        mcp = MCPConfig(servers=servers)
    
    return AppConfig(llm=llm, ltm=ltm, mcp=mcp)


