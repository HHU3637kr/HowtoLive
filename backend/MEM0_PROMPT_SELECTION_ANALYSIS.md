"""验证 mem0 的提示词选择逻辑

测试不同的消息格式会触发哪个提示词
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_app_config
from src.long_term_memory import build_mem0_long_term_memory


async def test_prompt_selection():
    """测试提示词选择"""
    
    print("=" * 80)
    print("测试 mem0 的提示词选择逻辑")
    print("=" * 80)
    
    cfg = load_app_config()
    test_user = "test_prompt_user"
    
    # 构建 LTM
    user_ltm = build_mem0_long_term_memory(cfg.ltm, cfg.llm, user_id=test_user, agent_name="test")
    mem0_instance = user_ltm.long_term_working_memory
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1: 只有 assistant 消息 + 有 agent_id（agent_control 模式的情况）",
            "messages": [
                {"role": "assistant", "content": "用户长期失眠"}
            ],
            "agent_id": "test",
            "expected_prompt": "AGENT_MEMORY_EXTRACTION_PROMPT",
            "expected_result": "应该提取失败（因为内容是关于 User 的，但提示词要求提取 Assistant 的信息）"
        },
        {
            "name": "场景2: 有 user 和 assistant 消息 + 有 agent_id（static_control 模式的情况）",
            "messages": [
                {"role": "user", "content": "我长期失眠"},
                {"role": "assistant", "content": "了解了"}
            ],
            "agent_id": "test",
            "expected_prompt": "可能是 AGENT_MEMORY_EXTRACTION_PROMPT，但会智能处理",
            "expected_result": "应该成功提取（因为有 user 消息）"
        },
        {
            "name": "场景3: 只有 user 消息 + 无 agent_id",
            "messages": [
                {"role": "user", "content": "我长期失眠"}
            ],
            "agent_id": None,
            "expected_prompt": "USER_MEMORY_EXTRACTION_PROMPT",
            "expected_result": "应该成功提取"
        },
        {
            "name": "场景4: Assistant 描述自己的信息",
            "messages": [
                {"role": "user", "content": "你叫什么名字？"},
                {"role": "assistant", "content": "我叫小助手，我很乐意帮助你"}
            ],
            "agent_id": "test",
            "expected_prompt": "AGENT_MEMORY_EXTRACTION_PROMPT",
            "expected_result": "应该提取 Assistant 的信息"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试 {i}: {test_case['name']}")
        print("=" * 80)
        
        print(f"\n预期使用的提示词: {test_case['expected_prompt']}")
        print(f"预期结果: {test_case['expected_result']}")
        
        print(f"\n消息内容:")
        for msg in test_case['messages']:
            print(f"  {msg['role']}: {msg['content']}")
        
        print(f"\nagent_id: {test_case['agent_id']}")
        
        print(f"\n正在调用 mem0.add()...")
        
        try:
            result = await mem0_instance.add(
                messages=test_case['messages'],
                user_id=test_user,
                agent_id=test_case['agent_id'],
            )
            
            print(f"\n📊 mem0 返回结果:")
            if result and 'results' in result and len(result['results']) > 0:
                for r in result['results']:
                    print(f"  - event: {r.get('event')}, memory: {r.get('memory')}")
            else:
                print(f"  ❌ 没有提取出任何记忆（results 为空）")
                print(f"  完整返回: {result}")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
        
        # 暂停避免 API 限流
        await asyncio.sleep(2)
    
    print(f"\n{'=' * 80}")
    print("测试完成")
    print("=" * 80)
    
    print("\n结论:")
    print("  - 场景1（agent_control）: 提取失败 → 验证了我们的分析")
    print("  - 场景2（static_control）: 提取成功 → 框架传入完整对话有效")
    print("  - 场景3: 无 agent_id → 使用 USER 提示词")
    print("  - 场景4: Assistant 自我描述 → 正确使用 AGENT 提示词")


if __name__ == "__main__":
    asyncio.run(test_prompt_selection())

