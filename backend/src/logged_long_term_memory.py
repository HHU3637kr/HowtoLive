"""带日志输出的长期记忆包装器

用于在 static_control 模式下追踪记忆的存储和检索操作
"""

from __future__ import annotations
from typing import Any
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LTM")

# 设置 mem0 相关日志级别为 DEBUG
mem0_logger = logging.getLogger("mem0.memory.main")
mem0_logger.setLevel(logging.DEBUG)

# 设置 mem0 的 LLM 相关日志
mem0_llm_logger = logging.getLogger("mem0.llms")
mem0_llm_logger.setLevel(logging.DEBUG)

# 设置 mem0 的工具相关日志
mem0_utils_logger = logging.getLogger("mem0.utils")
mem0_utils_logger.setLevel(logging.DEBUG)

# 添加控制台处理器以确保日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

for logger_obj in [mem0_logger, mem0_llm_logger, mem0_utils_logger]:
    if not logger_obj.handlers:
        logger_obj.addHandler(console_handler)

# 从环境变量读取是否启用详细模式（显示 LLM 的完整输入输出）
VERBOSE_MODE = os.getenv("LTM_VERBOSE", "false").lower() == "true"

if VERBOSE_MODE:
    logger.info("=" * 80)
    logger.info("🔍 详细调试模式已启用")
    logger.info("=" * 80)


class LoggedLongTermMemoryWrapper:
    """为长期记忆添加日志输出的包装器"""
    
    def __init__(self, ltm_instance: Any):
        """
        Args:
            ltm_instance: 原始的长期记忆实例（如 Mem0LongTermMemory）
        """
        self._ltm = ltm_instance
        logger.info(f"✓ 已创建带日志的长期记忆包装器: {type(ltm_instance).__name__}")
    
    def __getattr__(self, name: str) -> Any:
        """代理所有属性访问到原始 LTM 实例"""
        return getattr(self._ltm, name)
    
    async def retrieve(self, *args, **kwargs) -> list:
        """包装 retrieve 方法，添加日志"""
        logger.info("🔍 [检索] 开始从长期记忆检索...")
        
        # 尝试提取查询关键词（如果有的话）
        msg_arg = kwargs.get('msg') or (args[0] if args else None)
        if msg_arg:
            query_hint = str(msg_arg)[:100]  # 只显示前100个字符
            logger.info(f"   查询内容: {query_hint}")
        
        # 调用原始方法
        result = await self._ltm.retrieve(*args, **kwargs)
        
        # 记录结果
        if result:
            logger.info(f"✓ [检索] 找到 {len(result)} 条相关记忆")
            for i, item in enumerate(result, 1):
                memory_text = str(item)[:100]  # 只显示前100个字符
                logger.info(f"   记忆 {i}: {memory_text}")
        else:
            logger.info("✗ [检索] 未找到相关记忆")
        
        return result
    
    async def record(self, *args, **kwargs) -> Any:
        """包装 record 方法，添加日志"""
        logger.info("💾 [存储] 开始记录到长期记忆...")
        
        # 提取消息内容
        msgs_arg = kwargs.get('msgs') or (args[0] if args else None)
        if msgs_arg:
            if isinstance(msgs_arg, list):
                logger.info(f"   消息数量: {len(msgs_arg)}")
                for i, msg in enumerate(msgs_arg, 1):
                    content = getattr(msg, 'content', str(msg))[:50]
                    role = getattr(msg, 'role', getattr(msg, 'name', 'unknown'))
                    logger.info(f"   消息{i} ({role}): {content}...")
                    
                    # 详细模式：显示完整消息内容
                    if VERBOSE_MODE:
                        full_content = getattr(msg, 'content', str(msg))
                        logger.debug(f"   [详细] 消息{i}完整内容:\n{full_content}")
            else:
                logger.info(f"   内容: {str(msgs_arg)[:100]}")
        
        logger.info("   正在调用 mem0 的 LLM 分析消息内容...")
        logger.info("   ⏳ 请等待 LLM 决策...")
        
        # 调用原始方法
        result = await self._ltm.record(*args, **kwargs)
        
        # 记录结果
        logger.info(f"✓ [存储] 记录流程已完成")
        logger.info(f"")
        logger.info(f"   📊 查看上方的 'mem0.memory.main' 日志以了解 LLM 的决策：")
        logger.info(f"   - 'event': 'ADD' = 新增记忆（LLM 认为这是新的重要信息）")
        logger.info(f"   - 'event': 'UPDATE' = 更新记忆（LLM 认为需要更新已有记忆）")
        logger.info(f"   - 'event': 'NONE' = 无需操作（LLM 认为已存在或不重要）")
        logger.info(f"")
        
        if VERBOSE_MODE:
            logger.debug(f"   [详细] record() 返回值: {result}")
        
        return result


def wrap_with_logging(ltm_instance: Any | None) -> Any | None:
    """为长期记忆实例添加日志包装
    
    Args:
        ltm_instance: 原始的长期记忆实例，如果为 None 则返回 None
        
    Returns:
        带日志的包装实例，或 None
    """
    if ltm_instance is None:
        return None
    
    return LoggedLongTermMemoryWrapper(ltm_instance)

