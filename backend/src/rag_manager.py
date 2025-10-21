"""RAG 系统管理器

负责：
1. 管理嵌入模型（文本和多模态）
2. 为每个 Agent 创建和管理全局知识库和用户个人知识库
3. 提供知识库检索和添加接口
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from agentscope.rag import SimpleKnowledge, QdrantStore, Document
from agentscope.embedding import DashScopeTextEmbedding, DashScopeMultiModalEmbedding
from agentscope.tool import Toolkit

if TYPE_CHECKING:
    from .config import RAGConfig, RAGAgentConfig


class AgentKnowledgeBase:
    """单个 Agent 的知识库（包含全局 + 用户个人）"""
    
    def __init__(
        self,
        agent_name: str,
        user_id: str,
        global_knowledge: SimpleKnowledge,
        user_knowledge: SimpleKnowledge,
    ):
        """初始化 Agent 知识库
        
        Args:
            agent_name: Agent 名称
            user_id: 用户ID
            global_knowledge: 全局知识库实例
            user_knowledge: 用户个人知识库实例
        """
        self.agent_name = agent_name
        self.user_id = user_id
        self.global_kb = global_knowledge
        self.user_kb = user_knowledge
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[Document]:
        """从全局和用户知识库中检索，合并结果
        
        Args:
            query: 检索查询
            top_k: 返回的最大结果数
            
        Returns:
            检索到的文档列表，按相关性排序
        """
        # 从两个知识库检索
        global_results = await self.global_kb.retrieve(query, top_k=top_k//2)
        user_results = await self.user_kb.retrieve(query, top_k=top_k//2)
        
        # 合并并按分数排序
        all_results = global_results + user_results
        all_results.sort(key=lambda x: x.score or 0, reverse=True)
        
        return all_results[:top_k]
    
    async def add_to_global(self, documents: list[Document]):
        """添加文档到全局知识库
        
        Args:
            documents: 要添加的文档列表
        """
        await self.global_kb.add_documents(documents)
    
    async def add_to_user(self, documents: list[Document]):
        """添加文档到用户个人知识库
        
        Args:
            documents: 要添加的文档列表
        """
        await self.user_kb.add_documents(documents)
    
    async def retrieve_knowledge(self, query: str, limit: int = 5, score_threshold: float = 0.5):
        """搜索知识库（混合搜索全局和用户知识库）
        
        这个方法复用 SimpleKnowledge.retrieve_knowledge() 的实现，
        同时搜索全局和用户知识库，并合并结果。
        
        Args:
            query: 检索查询，应该具体明确
            limit: 返回的最大结果数
            score_threshold: 相关性分数阈值（0-1），只返回分数高于此值的结果
            
        Returns:
            ToolResponse 对象，包含检索到的知识片段
        """
        from agentscope.tool import ToolResponse
        from agentscope.message import TextBlock
        
        # 分别从两个知识库检索
        global_response = await self.global_kb.retrieve_knowledge(
            query=query,
            limit=limit // 2,
            score_threshold=score_threshold,
        )
        
        user_response = await self.user_kb.retrieve_knowledge(
            query=query,
            limit=limit // 2,
            score_threshold=score_threshold,
        )
        
        # 合并两个 ToolResponse 的内容
        combined_content = []
        
        # 添加全局知识库结果
        if global_response.content:
            combined_content.append(
                TextBlock(
                    type="text",
                    text="【全局知识库】\n",
                )
            )
            combined_content.extend(global_response.content)
        
        # 添加用户知识库结果
        if user_response.content:
            combined_content.append(
                TextBlock(
                    type="text",
                    text="\n【个人知识库】\n",
                )
            )
            combined_content.extend(user_response.content)
        
        # 如果都没有结果
        if not combined_content:
            combined_content = [
                TextBlock(
                    type="text",
                    text=f"未找到与'{query}'相关的知识。",
                )
            ]
        
        return ToolResponse(content=combined_content)
    
    async def add_knowledge_to_user(self, text: str):
        """添加文本知识到用户个人知识库（用于工具调用）
        
        这是 add_to_user 方法的简化版本，接受文本字符串而不是 Document 对象。
        
        Args:
            text: 要添加的文本内容
            
        Returns:
            ToolResponse 对象
        """
        from agentscope.tool import ToolResponse
        from agentscope.message import TextBlock
        from agentscope.rag import TextReader
        
        try:
            # 使用 TextReader 将文本转换为 Document
            reader = TextReader(chunk_size=512, split_by="paragraph")
            docs = await reader(text=text)
            
            # 添加到用户知识库
            await self.add_to_user(docs)
            
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"成功将内容添加到个人知识库（{len(docs)} 个文档块）。",
                    ),
                ],
            )
        except Exception as e:
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"添加失败：{str(e)}",
                    ),
                ],
            )


class RAGManager:
    """RAG 系统管理器"""
    
    def __init__(self, rag_config: RAGConfig):
        """初始化 RAG 管理器
        
        Args:
            rag_config: RAG 配置对象
        """
        self.config = rag_config
        self.embedding_model = None
        self.multimodal_embedding_model = None
        self.global_knowledges: dict[str, SimpleKnowledge] = {}
        self.user_knowledges: dict[str, AgentKnowledgeBase] = {}
    
    async def initialize(self):
        """初始化嵌入模型和全局知识库"""
        print("[RAG] 初始化 RAG 系统...")
        
        # 创建嵌入模型
        self._create_embedding_models()
        
        # 为每个启用的 Agent 创建全局知识库
        for agent_name, agent_cfg in self.config.agents.items():
            if agent_cfg.enabled:
                await self._create_global_knowledge(agent_name, agent_cfg)
        
        print("[RAG] ✓ RAG 系统初始化完成")
    
    def _create_embedding_models(self):
        """创建文本和多模态嵌入模型"""
        # 创建文本嵌入模型
        emb_cfg = self.config.embedding
        api_key = os.getenv(emb_cfg.api_key_env)
        
        if emb_cfg.provider == "qwen":
            self.embedding_model = DashScopeTextEmbedding(
                api_key=api_key,
                model_name=emb_cfg.model_name,
                dimensions=emb_cfg.dimensions,
            )
            print(f"[RAG]   ✓ 文本嵌入模型已创建: {emb_cfg.model_name}")
        
        # 创建多模态嵌入模型
        mm_emb_cfg = self.config.multimodal_embedding
        if mm_emb_cfg.provider == "qwen":
            self.multimodal_embedding_model = DashScopeMultiModalEmbedding(
                api_key=api_key,
                model_name=mm_emb_cfg.model_name,
                dimensions=mm_emb_cfg.dimensions,
            )
            print(f"[RAG]   ✓ 多模态嵌入模型已创建: {mm_emb_cfg.model_name}")
    
    async def _create_global_knowledge(self, agent_name: str, agent_cfg: RAGAgentConfig):
        """为指定 Agent 创建全局知识库
        
        Args:
            agent_name: Agent 名称
            agent_cfg: Agent 配置
        """
        # 获取向量存储配置
        vector_store_cfg = self.config.vector_store
        location = vector_store_cfg.get("location", "./data/vector_db")
        
        # 创建向量存储
        store = QdrantStore(
            location=location,
            collection_name=agent_cfg.global_kb.collection_name,
            dimensions=self.config.embedding.dimensions,
        )
        
        # 创建知识库
        knowledge = SimpleKnowledge(
            embedding_model=self.embedding_model,
            embedding_store=store,
        )
        
        self.global_knowledges[agent_name] = knowledge
        print(f"[RAG]   ✓ {agent_name} 全局知识库已创建")
    
    def _create_user_knowledge(self, agent_name: str, user_id: str):
        """为指定 Agent 和用户创建个人知识库
        
        Args:
            agent_name: Agent 名称
            user_id: 用户ID
        """
        agent_cfg = self.config.agents[agent_name]
        
        # 替换用户ID占位符
        collection_name = agent_cfg.user_kb.collection_name.replace("{user_id}", user_id)
        
        # 获取向量存储配置
        vector_store_cfg = self.config.vector_store
        location = vector_store_cfg.get("location", "./data/vector_db")
        
        # 创建向量存储
        store = QdrantStore(
            location=location,
            collection_name=collection_name,
            dimensions=self.config.embedding.dimensions,
        )
        
        # 创建知识库
        knowledge = SimpleKnowledge(
            embedding_model=self.embedding_model,
            embedding_store=store,
        )
        
        # 创建 AgentKnowledgeBase
        key = f"{user_id}_{agent_name}"
        self.user_knowledges[key] = AgentKnowledgeBase(
            agent_name=agent_name,
            user_id=user_id,
            global_knowledge=self.global_knowledges[agent_name],
            user_knowledge=knowledge,
        )
    
    def get_agent_kb(
        self,
        agent_name: str,
        user_id: str,
    ) -> AgentKnowledgeBase:
        """获取或创建指定 Agent 和用户的知识库
        
        Args:
            agent_name: Agent 名称
            user_id: 用户ID
            
        Returns:
            AgentKnowledgeBase 实例
        """
        key = f"{user_id}_{agent_name}"
        
        if key not in self.user_knowledges:
            self._create_user_knowledge(agent_name, user_id)
        
        return self.user_knowledges[key]
    
    def register_tools_to_toolkit(
        self,
        agent_name: str,
        user_id: str,
        toolkit: Toolkit,
    ):
        """将知识库工具注册到 Toolkit
        
        Args:
            agent_name: Agent 名称
            user_id: 用户ID
            toolkit: 要注册到的工具集
        """
        kb = self.get_agent_kb(agent_name, user_id)
        
        # 构建更详细的工具描述
        agent_descriptions = {
            "howtoeat": "饮食与营养",
            "howtocook": "烹饪方法",
            "howtosleep": "睡眠改善",
            "howtoexercise": "运动训练",
        }
        domain = agent_descriptions.get(agent_name, agent_name)
        
        # 注册检索工具
        toolkit.register_tool_function(
            kb.retrieve_knowledge,
            func_description=f"搜索{domain}领域的知识库。当用户询问专业知识、方法、技巧时使用。",
        )
        
        # 注册添加工具
        toolkit.register_tool_function(
            kb.add_knowledge_to_user,
            func_description=f"将重要信息添加到用户的{domain}个人知识库。仅在用户分享有价值的经验、笔记时使用。",
        )

