"""导入知识到全局知识库的脚本

使用方法：
    python backend/tools/import_knowledge.py <agent_name> <data_path> [data_type]
    
示例：
    python backend/tools/import_knowledge.py howtoeat ./data/nutrition.txt text
    python backend/tools/import_knowledge.py howtocook ./data/recipes.pdf pdf
    python backend/tools/import_knowledge.py howtosleep ./data/sleep_tips.png image
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.config import load_app_config
from backend.src.rag_manager import RAGManager
from agentscope.rag import TextReader, PDFReader, ImageReader


async def import_knowledge(
    agent_name: str,
    data_path: str,
    data_type: str = "text",
):
    """导入知识到指定 Agent 的全局知识库
    
    Args:
        agent_name: Agent 名称 (howtoeat, howtocook, howtosleep, howtoexercise)
        data_path: 数据文件路径
        data_type: 数据类型 (text, pdf, image)
    """
    print("=" * 80)
    print(f"导入知识到 {agent_name} 的全局知识库")
    print("=" * 80)
    
    # 加载配置
    cfg = load_app_config("backend/config")
    
    if not cfg.rag or not cfg.rag.enabled:
        print("❌ RAG 未启用，请在 backend/config/rag.yaml 中启用")
        return
    
    if agent_name not in cfg.rag.agents:
        print(f"❌ 未知的 Agent: {agent_name}")
        print(f"可用的 Agent: {', '.join(cfg.rag.agents.keys())}")
        return
    
    # 初始化 RAG 管理器
    print("\n[1] 初始化 RAG 管理器...")
    rag_manager = RAGManager(cfg.rag)
    await rag_manager.initialize()
    
    # 读取数据
    print(f"\n[2] 读取数据文件: {data_path}")
    print(f"    数据类型: {data_type}")
    
    documents = []
    try:
        if data_type == "text":
            # 读取文本文件
            reader_cfg = cfg.rag.readers.get("text", {})
            reader = TextReader(
                chunk_size=reader_cfg.get("chunk_size", 512),
                split_by=reader_cfg.get("split_by", "paragraph"),
            )
            with open(data_path, "r", encoding="utf-8") as f:
                text = f.read()
            documents = await reader(text=text)
            
        elif data_type == "pdf":
            # 读取 PDF 文件
            reader_cfg = cfg.rag.readers.get("pdf", {})
            reader = PDFReader(
                chunk_size=reader_cfg.get("chunk_size", 512),
            )
            documents = await reader(pdf_path=data_path)
            
        elif data_type == "image":
            # 读取图片文件
            reader = ImageReader()
            documents = await reader(image_url=data_path)
            
        else:
            print(f"❌ 不支持的数据类型: {data_type}")
            print("   支持的类型: text, pdf, image")
            return
        
        print(f"✓ 成功读取，共 {len(documents)} 个文档块")
        
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return
    
    # 添加到全局知识库
    print(f"\n[3] 添加到 {agent_name} 的全局知识库...")
    try:
        global_kb = rag_manager.global_knowledges[agent_name]
        await global_kb.add_documents(documents)
        print(f"✓ 成功添加 {len(documents)} 个文档块到全局知识库")
        
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return
    
    print("\n" + "=" * 80)
    print("✓ 导入完成")
    print("=" * 80)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    agent_name = sys.argv[1]
    data_path = sys.argv[2]
    data_type = sys.argv[3] if len(sys.argv) > 3 else "text"
    
    asyncio.run(import_knowledge(agent_name, data_path, data_type))


if __name__ == "__main__":
    main()

