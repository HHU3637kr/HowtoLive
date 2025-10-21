"""清空知识库的脚本

使用方法：
    # 清空全局知识库
    python backend/tools/clear_knowledge.py <agent_name>
    
    # 清空用户知识库
    python backend/tools/clear_knowledge.py <agent_name> --user <user_id>
    
示例：
    python backend/tools/clear_knowledge.py howtoeat
    python backend/tools/clear_knowledge.py howtocook --user Rking
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.config import load_app_config


async def clear_knowledge(agent_name: str, user_id: str = None):
    """清空指定知识库
    
    Args:
        agent_name: Agent 名称
        user_id: 用户ID（可选，如果提供则清空用户知识库）
    """
    kb_type = "用户" if user_id else "全局"
    print("=" * 80)
    print(f"清空 {agent_name} 的{kb_type}知识库")
    if user_id:
        print(f"用户ID: {user_id}")
    print("=" * 80)
    
    # 确认操作
    confirm = input(f"\n⚠️  确定要清空{kb_type}知识库吗？此操作不可恢复！(yes/no): ")
    if confirm.lower() != "yes":
        print("已取消操作")
        return
    
    # 加载配置
    cfg = load_app_config("backend/config")
    
    if not cfg.rag or not cfg.rag.enabled:
        print("❌ RAG 未启用")
        return
    
    if agent_name not in cfg.rag.agents:
        print(f"❌ 未知的 Agent: {agent_name}")
        return
    
    # 获取 collection 名称
    agent_cfg = cfg.rag.agents[agent_name]
    if user_id:
        collection_name = agent_cfg.user_kb.collection_name.replace("{user_id}", user_id)
    else:
        collection_name = agent_cfg.global_kb.collection_name
    
    print(f"\n[1] 连接到向量数据库...")
    print(f"    Collection: {collection_name}")
    
    try:
        from agentscope.rag import QdrantStore
        
        # 获取向量数据库配置
        vector_store_cfg = cfg.rag.vector_store
        location = vector_store_cfg.get("location", "http://localhost:6333")
        
        # 连接到 Qdrant
        from qdrant_client import QdrantClient
        # 判断是本地文件还是网络连接
        if location.startswith("http"):
            client = QdrantClient(url=location)
            print(f"    连接地址: {location}")
        else:
            client = QdrantClient(path=location)
            print(f"    本地路径: {location}")
        
        # 检查 collection 是否存在
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if collection_name not in collection_names:
            print(f"\n⚠️  Collection '{collection_name}' 不存在，无需清空")
            return
        
        print(f"\n[2] 删除 collection...")
        client.delete_collection(collection_name)
        print(f"✓ 成功删除 collection: {collection_name}")
        
    except Exception as e:
        print(f"❌ 清空失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("✓ 清空完成")
    print("=" * 80)
    print("\n提示：下次访问该知识库时会自动重新创建空的 collection")


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
    
    asyncio.run(clear_knowledge(agent_name, user_id))


if __name__ == "__main__":
    main()

