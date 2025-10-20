from __future__ import annotations

from typing import Any

try:
    # AgentScope imports (names may vary by version; adjust if needed)
    from agentscope.model import DashScopeChatModel
    from agentscope.formatter import DashScopeChatFormatter
except Exception as e:  # pragma: no cover - allow import-time missing deps
    DashScopeChatModel = None  # type: ignore
    DashScopeChatFormatter = None  # type: ignore

from .config import LLMConfig


class ModelBundle:
    def __init__(self, model: Any, formatter: Any) -> None:
        self.model = model
        self.formatter = formatter


def build_chat_model(llm: LLMConfig, *, force_stream: bool | None = None) -> ModelBundle:
    """Create chat model + formatter for Qwen(DashScope).

    force_stream: override streaming for specific agents (e.g., router=False)
    """
    if llm.provider != "qwen":
        raise ValueError("Only qwen provider is supported in v1")
    if DashScopeChatModel is None or DashScopeChatFormatter is None:
        raise RuntimeError("agentscope is required for model creation")

    stream = llm.streaming if force_stream is None else bool(force_stream)
    # DashScopeChatModel commonly accepts: model_name, api_key, stream
    # Generation params like temperature/max_tokens can be controlled elsewhere per AgentScope version
    model = DashScopeChatModel(
        model_name=llm.qwen_model,
        api_key=llm.qwen_api_key,
        stream=stream,
    )
    formatter = DashScopeChatFormatter()
    return ModelBundle(model=model, formatter=formatter)


