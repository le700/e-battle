"""
MemoryStore - 好友记忆库系统

使用RAG（Retrieval-Augmented Generation）技术实现长期记忆
基于Chroma向量数据库存储聊天记录的向量表示
支持上下文相关的记忆检索
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    sender: str
    timestamp: datetime
    conversation_id: str
    metadata: Dict[str, Any]


class MemoryStore:
    """
    记忆库存储类
    
    使用Chroma向量数据库存储和检索聊天记忆
    支持：
    - 存储聊天记录到向量数据库
    - 基于语义相似性检索相关记忆
    - 支持对话历史管理
    - 支持长期记忆和短期记忆
    """
    
    def __init__(self, friend_name: str, persist_dir: Optional[Path] = None):
        """
        初始化记忆库
        
        Args:
            friend_name: 好友名称，用于区分不同好友的记忆库
            persist_dir: 持久化目录，默认为 data/memory/{friend_name}
        """
        self.friend_name = friend_name
        if persist_dir is None:
            persist_dir = Path(f"data/memory/{friend_name}")
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_chroma()
    
    def _init_chroma(self):
        """初始化Chroma向量数据库"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 创建或获取集合
            self.collection = self.client.get_or_create_collection(
                name=f"friend_{self.friend_name}",
                metadata={"description": f"Memory store for {self.friend_name}"}
            )
            
            self.has_chroma = True
        except ImportError:
            self.has_chroma = False
            print("⚠️ Chroma未安装，使用简单文件存储模式")
    
    def add_memory(self, content: str, sender: str, conversation_id: str = "default", 
                   metadata: Optional[Dict] = None):
        """
        添加记忆到数据库
        
        Args:
            content: 记忆内容
            sender: 发送者
            conversation_id: 对话ID，用于分组
            metadata: 额外元数据
        """
        if not self.has_chroma:
            self._add_memory_file(content, sender, conversation_id, metadata)
            return
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "sender": sender,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        })
        
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[f"{conversation_id}_{datetime.now().timestamp()}"]
        )
    
    def _add_memory_file(self, content: str, sender: str, conversation_id: str, metadata: Dict):
        """文件模式下添加记忆"""
        memory_file = self.persist_dir / "memories.json"
        
        memories = []
        if memory_file.exists():
            with open(memory_file, "r", encoding="utf-8") as f:
                memories = json.load(f)
        
        memories.append({
            "id": f"{conversation_id}_{datetime.now().timestamp()}",
            "content": content,
            "sender": sender,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)
    
    def retrieve_memories(self, query: str, top_k: int = 5, 
                         conversation_id: Optional[str] = None) -> List[Dict]:
        """
        检索相关记忆
        
        Args:
            query: 查询文本
            top_k: 返回条数
            conversation_id: 可选，限定对话范围
        
        Returns:
            相关记忆列表，按相似度排序
        """
        if not self.has_chroma:
            return self._retrieve_memories_file(query, top_k, conversation_id)
        
        where = None
        if conversation_id:
            where = {"conversation_id": conversation_id}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )
        
        memories = []
        for i in range(len(results["ids"][0])):
            memories.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return memories
    
    def _retrieve_memories_file(self, query: str, top_k: int, conversation_id: str) -> List[Dict]:
        """文件模式下检索记忆（简单匹配）"""
        memory_file = self.persist_dir / "memories.json"
        
        if not memory_file.exists():
            return []
        
        with open(memory_file, "r", encoding="utf-8") as f:
            memories = json.load(f)
        
        # 简单匹配：包含关键词的记忆
        filtered = []
        query_words = query.lower().split()
        
        for memory in memories:
            if conversation_id and memory["conversation_id"] != conversation_id:
                continue
            
            content_lower = memory["content"].lower()
            match_count = sum(1 for word in query_words if word in content_lower)
            
            if match_count > 0:
                filtered.append({
                    "content": memory["content"],
                    "metadata": memory.get("metadata", {})
                })
        
        return filtered[:top_k]
    
    def add_conversation_history(self, messages: List[Dict], conversation_id: str = "default"):
        """
        添加对话历史到记忆库
        
        Args:
            messages: 消息列表，每条包含 content, sender
            conversation_id: 对话ID
        """
        for msg in messages:
            self.add_memory(
                content=msg["content"],
                sender=msg["sender"],
                conversation_id=conversation_id
            )
    
    def get_recent_memories(self, conversation_id: str = "default", limit: int = 20) -> List[Dict]:
        """
        获取最近的记忆
        
        Args:
            conversation_id: 对话ID
            limit: 返回条数
        
        Returns:
            最近的记忆列表
        """
        if not self.has_chroma:
            memory_file = self.persist_dir / "memories.json"
            if not memory_file.exists():
                return []
            
            with open(memory_file, "r", encoding="utf-8") as f:
                memories = json.load(f)
            
            if conversation_id:
                memories = [m for m in memories if m["conversation_id"] == conversation_id]
            
            # 按时间排序
            memories.sort(key=lambda x: x["timestamp"], reverse=True)
            return memories[:limit]
        
        # Chroma模式：查询最近的记忆
        results = self.collection.query(
            query_texts=["recent"],
            n_results=limit,
            where={"conversation_id": conversation_id} if conversation_id else None
        )
        
        return [{
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i]
        } for i in range(len(results["ids"][0]))]
    
    def clear_memory(self, conversation_id: Optional[str] = None):
        """
        清除记忆
        
        Args:
            conversation_id: 可选，清除特定对话的记忆；不指定则清除所有
        """
        if not self.has_chroma:
            memory_file = self.persist_dir / "memories.json"
            if memory_file.exists():
                if conversation_id:
                    with open(memory_file, "r", encoding="utf-8") as f:
                        memories = json.load(f)
                    memories = [m for m in memories if m["conversation_id"] != conversation_id]
                    with open(memory_file, "w", encoding="utf-8") as f:
                        json.dump(memories, f, ensure_ascii=False, indent=2)
                else:
                    memory_file.unlink()
            return
        
        if conversation_id:
            # 删除特定对话的记忆
            results = self.collection.get(where={"conversation_id": conversation_id})
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
        else:
            # 重置整个集合
            self.client.reset()
            self._init_chroma()
    
    def get_memory_count(self) -> int:
        """获取记忆总数"""
        if not self.has_chroma:
            memory_file = self.persist_dir / "memories.json"
            if not memory_file.exists():
                return 0
            with open(memory_file, "r", encoding="utf-8") as f:
                return len(json.load(f))
        
        return self.collection.count()


class RAGMemoryManager:
    """
    RAG记忆管理器
    
    整合记忆库和好友画像，为AI提供上下文感知能力
    """
    
    def __init__(self, friend_name: str):
        """
        初始化RAG记忆管理器
        
        Args:
            friend_name: 好友名称
        """
        self.friend_name = friend_name
        self.memory_store = MemoryStore(friend_name)
    
    def build_context_for_prompt(self, current_query: str, conversation_id: str = "default",
                                include_recent: int = 10, include_relevant: int = 5) -> str:
        """
        为提示词构建上下文
        
        Args:
            current_query: 当前查询
            conversation_id: 对话ID
            include_recent: 包含最近消息数
            include_relevant: 包含相关记忆数
        
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        # 获取最近对话
        recent_memories = self.memory_store.get_recent_memories(conversation_id, include_recent)
        if recent_memories:
            context_parts.append("## 最近对话历史")
            for i, memory in enumerate(reversed(recent_memories), 1):
                sender = memory["metadata"].get("sender", "Unknown")
                content = memory["content"]
                context_parts.append(f"{sender}: {content}")
        
        # 获取相关记忆
        relevant_memories = self.memory_store.retrieve_memories(current_query, include_relevant)
        if relevant_memories:
            context_parts.append("\n## 相关记忆")
            for i, memory in enumerate(relevant_memories, 1):
                content = memory["content"]
                context_parts.append(f"- {content}")
        
        return "\n".join(context_parts)
    
    def update_memory(self, user_message: str, ai_response: str, conversation_id: str = "default"):
        """
        更新记忆库，添加新的对话
        
        Args:
            user_message: 用户消息
            ai_response: AI响应
            conversation_id: 对话ID
        """
        self.memory_store.add_memory(
            content=user_message,
            sender="user",
            conversation_id=conversation_id
        )
        
        self.memory_store.add_memory(
            content=ai_response,
            sender=self.friend_name,
            conversation_id=conversation_id
        )
    
    def get_memory_summary(self) -> Dict:
        """获取记忆库摘要"""
        return {
            "friend_name": self.friend_name,
            "total_memories": self.memory_store.get_memory_count(),
            "has_vector_db": self.memory_store.has_chroma
        }