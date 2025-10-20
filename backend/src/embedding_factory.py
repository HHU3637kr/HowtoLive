from __future__ import annotations

import os
from typing import Any

try:
    from agentscope.embedding import DashScopeTextEmbedding
except Exception:
    DashScopeTextEmbedding = None  # type: ignore

from .config import LTMConfig, LLMConfig


def _resolve_api_key(env_name: str | None, fallback_key: str | None) -> str | None:
    if env_name:
        v = os.getenv(env_name)
        if v:
            return v
    return fallback_key


def build_text_embedding(ltm_cfg: LTMConfig | None, fallback_llm: LLMConfig) -> Any | None:
    """Construct DashScopeTextEmbedding from LTM config.

    Returns None if embedding is not configured or agentscope is missing.
    """
    if ltm_cfg is None or ltm_cfg.embedding is None:
        return None
    if DashScopeTextEmbedding is None:
        return None
    if ltm_cfg.embedding.provider != "qwen":
        raise ValueError("Only qwen embedding provider is supported in v1")

    api_key = _resolve_api_key(ltm_cfg.embedding.api_key_env, fallback_llm.qwen_api_key)
    return DashScopeTextEmbedding(
        model_name=ltm_cfg.embedding.model_name,
        api_key=api_key,
    )


