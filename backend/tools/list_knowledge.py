"""查看知识库内容的脚本

使用方法：
    # 列出全局知识库
    python backend/tools/list_knowledge.py <agent_name>
    
    # 列出用户知识库
    python backend/tools/list_knowledge.py <agent_name> --user <user_id>
    
示例：
    python backend/tools/list_knowledge.py howtoeat
    python backend/tools/list_knowledge.py howtocook --user Rking
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.config import load_app_config
from backend.src.rag_manager import RAGManager


async def list_knowledge(agent_name: str, user_id: str = None):
    """列出知识库中的文档
    
    Args:
        agent_name: Agent 名称
        user_id: 用户ID（可选，如果提供则查看用户知识库）
    """
    kb_type = "用户" if user_id else "全局"
    print("=" * 80)
    print(f"查看 {agent_name} 的{kb_type}知识库")
    if user_id:
        print(f"用户ID: {user_id}")
    print("=" * 80)
    
    # 加载配置
    cfg = load_app_config("backend/config")
    
    if not cfg.rag or not cfg.rag.enabled:
        print("❌ RAG 未启用")
        return
    
    if agent_name not in cfg.rag.agents:
        print(f"❌ 未知的 Agent: {agent_name}")
        return
    
    # 初始化 RAG 管理器
    print("\n[1] 初始化 RAG 管理器...")
    rag_manager = RAGManager(cfg.rag)
    await rag_manager.initialize()
    
    # 获取知识库
    if user_id:
        kb = rag_manager.get_agent_kb(agent_name, user_id).user_kb
    else:
        kb = rag_manager.global_knowledges[agent_name]
    
    # 执行一次检索来获取知识库信息
    print(f"\n[2] 检索知识库内容...")
    try:
        # 使用一个通用查询来获取一些文档
        results = await kb.retrieve(query="", top_k=10)
        
        if not results:
            print(f"\n⚠️  {kb_type}知识库为空")
        else:
            print(f"\n✓ 找到 {len(results)} 个文档（最多显示 10 个）:")
            print("-" * 80)
            
            for i, doc in enumerate(results, 1):
                print(f"\n文档 {i}:")
                print(f"  分数: {doc.score:.4f if doc.score else 'N/A'}")
                
                content = doc.metadata.get("content", "")
                if hasattr(content, "text"):
                    # TextBlock
                    preview = content.text[:200]
                    print(f"  内容: {preview}{'...' if len(content.text) > 200 else ''}")
                elif hasattr(content, "url"):
                    # ImageBlock
                    print(f"  类型: 图片")
                    print(f"  URL: {content.url}")
                else:
                    print(f"  内容: {str(content)[:200]}")
                
                print(f"  文档ID: {doc.metadata.get('doc_id', 'N/A')}")
                print(f"  块ID: {doc.metadata.get('chunk_id', 'N/A')}/{doc.metadata.get('total_chunks', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("✓ 查看完成")
    print("=" * 80)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    agent_name = sys.argv[1]
    user_id = None
    
    # 解析参数
    if "--user" in sys.argv:
        user_idx = sys.argv.index("--user")
        if user_idx + 1 < len(sys.argv):
            user_id = sys.argv[user_idx + 1]
    
    asyncio.run(list_knowledge(agent_name, user_id))


if __name__ == "__main__":
    main()

