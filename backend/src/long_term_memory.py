from __future__ import annotations

import os
from typing import Any

try:
    from agentscope.memory import Mem0LongTermMemory
    from agentscope.model import DashScopeChatModel
except Exception:
    Mem0LongTermMemory = None  # type: ignore
    DashScopeChatModel = None  # type: ignore

from .config import LTMConfig, LLMConfig
from .embedding_factory import build_text_embedding


def _resolve_api_key(env_name: str | None, fallback_key: str | None) -> str | None:
    if env_name:
        v = os.getenv(env_name)
        if v:
            return v
    return fallback_key


def build_mem0_long_term_memory(
    ltm_cfg: LTMConfig | None,
    fallback_llm: LLMConfig,
    *,
    user_id: str,
    agent_name: str = "howtolive",
) -> Any | None:
    """Create Mem0LongTermMemory for the given user_id.

    Returns None if LTM is disabled or agentscope is missing.
    Storage path: backend/.ltm_storage/{user_id}/ when on_disk=True
    """
    if ltm_cfg is None or not ltm_cfg.enabled:
        return None
    if Mem0LongTermMemory is None or DashScopeChatModel is None:
        return None
    if ltm_cfg.provider != "mem0":
        raise ValueError("Only mem0 long-term memory is supported in v1")

    # Chat model for memory ops
    chat_cfg = ltm_cfg.chat_model
    if chat_cfg is None:
        raise ValueError("LTM chat_model config is required")
    api_key = _resolve_api_key(chat_cfg.api_key_env, fallback_llm.qwen_api_key)
    chat_model = DashScopeChatModel(
        model_name=chat_cfg.model_name,
        api_key=api_key,
        stream=bool(chat_cfg.stream),
    )

    # Embedding model
    embedding_model = build_text_embedding(ltm_cfg, fallback_llm)

    # Build mem0_config to connect to Qdrant server (Docker/remote mode)
    # This avoids file locking issues with local on-disk mode
    mem0_config = None
    try:
        from mem0.configs.base import MemoryConfig

        # Use Qdrant server mode (host/port) instead of local file mode
        # This supports concurrent access from multiple agent instances
        vector_store_config: dict[str, Any] = {
            "provider": "qdrant",
            "config": {
                "host": "localhost",
                "port": 6333,
                "collection_name": f"mem0_{user_id}",  # Per-user collection
                "on_disk": False,
            },
        }

        mem0_config = MemoryConfig(vector_store=vector_store_config)
    except Exception:
        # Fallback: pass None and use AgentScope's default logic
        mem0_config = None

    # When mem0_config is provided, do NOT pass on_disk parameter
    # as it's already configured in mem0_config.vector_store
    # 注意：不传入 agent_name，以确保 mem0 使用 USER_MEMORY_EXTRACTION_PROMPT
    # 而不是 AGENT_MEMORY_EXTRACTION_PROMPT（后者只提取 Assistant 自己的信息）
    return Mem0LongTermMemory(
        agent_name=None,  # 不传入 agent_name，避免使用 AGENT 提示词
        user_name=user_id,
        model=chat_model,
        embedding_model=embedding_model,
        mem0_config=mem0_config,
    )


