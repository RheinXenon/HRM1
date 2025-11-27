"""
Agent记忆系统
实现三层记忆架构：短期记忆、情节记忆、语义记忆
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import pickle
from pathlib import Path
from loguru import logger
from collections import defaultdict


@dataclass
class WorkingMemory:
    """短期记忆（Working Memory）- 当前面试会话"""
    session_id: str
    conversation_history: List[Dict] = field(default_factory=list)
    current_evaluations: List[Dict] = field(default_factory=list)
    candidate_profile: Dict = field(default_factory=dict)
    real_time_observations: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_conversation(self, role: str, content: Any, **metadata):
        """添加对话记录"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **metadata
        })
    
    def add_evaluation(self, evaluation: Dict):
        """添加评估结果"""
        self.current_evaluations.append({
            **evaluation,
            "timestamp": datetime.now().isoformat()
        })
    
    def clear(self):
        """清空短期记忆"""
        self.conversation_history.clear()
        self.current_evaluations.clear()
        self.real_time_observations.clear()


@dataclass
class EpisodicMemory:
    """情节记忆（Episodic Memory）- 历史面试片段"""
    memory_id: str
    interview_id: str
    timestamp: datetime
    
    # 场景信息
    scenario_type: str  # 面试场景类型
    question_category: str
    skill_area: str
    
    # 关键片段
    question: str
    answer: str
    evaluation: Dict
    
    # 策略和效果
    strategy_used: str  # 使用的策略（追问/不追问等）
    effectiveness: float  # 效果评分 0-1
    
    # 标签和分类
    tags: List[str] = field(default_factory=list)
    is_successful: bool = True  # 是否成功案例
    is_failure: bool = False  # 是否失败案例
    
    # 额外信息
    candidate_characteristics: Dict = field(default_factory=dict)
    lessons_learned: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EpisodicMemory':
        """从字典创建"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class SemanticMemory:
    """语义记忆（Semantic Memory）- 通用知识和规律"""
    memory_id: str
    
    # 知识类型
    knowledge_type: str  # "evaluation_pattern" / "question_template" / "candidate_pattern" / "best_practice"
    
    # 知识内容
    pattern_name: str
    pattern_description: str
    applicable_conditions: List[str] = field(default_factory=list)
    
    # 统计信息
    usage_count: int = 0
    success_rate: float = 0.0
    confidence: float = 0.5
    
    # 数据支持
    supporting_examples: List[str] = field(default_factory=list)  # 支持的情节记忆ID列表
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_statistics(self, success: bool):
        """更新使用统计"""
        self.usage_count += 1
        # 使用指数移动平均更新成功率
        alpha = 0.3
        self.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * self.success_rate
        self.confidence = min(1.0, self.usage_count / 20.0)  # 20次后达到最大置信度
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SemanticMemory':
        """从字典创建"""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


class MemorySystem:
    """三层记忆系统管理器"""
    
    def __init__(self, storage_dir: str = "data/memory"):
        """
        初始化记忆系统
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前会话的短期记忆
        self.working_memory: Optional[WorkingMemory] = None
        
        # 情节记忆存储
        self.episodic_memories: List[EpisodicMemory] = []
        self.episodic_index: Dict[str, List[int]] = defaultdict(list)  # 索引：skill_area -> memory indices
        
        # 语义记忆存储
        self.semantic_memories: Dict[str, SemanticMemory] = {}
        
        # 加载持久化的记忆
        self._load_memories()
        
        logger.info(f"💭 记忆系统初始化完成: {len(self.episodic_memories)} 条情节记忆, "
                   f"{len(self.semantic_memories)} 条语义记忆")
    
    # ==================== 短期记忆管理 ====================
    
    def create_working_memory(self, session_id: str, candidate_profile: Dict) -> WorkingMemory:
        """创建新的短期记忆（新面试会话）"""
        self.working_memory = WorkingMemory(
            session_id=session_id,
            candidate_profile=candidate_profile
        )
        logger.info(f"🧠 创建短期记忆: {session_id}")
        return self.working_memory
    
    def get_working_memory(self) -> Optional[WorkingMemory]:
        """获取当前短期记忆"""
        return self.working_memory
    
    def clear_working_memory(self):
        """清空短期记忆（面试结束）"""
        if self.working_memory:
            logger.info(f"🗑️  清空短期记忆: {self.working_memory.session_id}")
            self.working_memory = None
    
    # ==================== 情节记忆管理 ====================
    
    def add_episodic_memory(self, memory: EpisodicMemory):
        """添加情节记忆"""
        # 添加到列表
        index = len(self.episodic_memories)
        self.episodic_memories.append(memory)
        
        # 更新索引
        self.episodic_index[memory.skill_area].append(index)
        for tag in memory.tags:
            self.episodic_index[f"tag:{tag}"].append(index)
        
        logger.debug(f"📝 添加情节记忆: {memory.memory_id} ({memory.skill_area})")
    
    def retrieve_episodic_memories(
        self,
        skill_area: Optional[str] = None,
        scenario_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5,
        only_successful: bool = False
    ) -> List[EpisodicMemory]:
        """
        检索相关的情节记忆
        
        Args:
            skill_area: 技能领域
            scenario_type: 场景类型
            tags: 标签列表
            limit: 返回数量限制
            only_successful: 只返回成功案例
            
        Returns:
            相关的情节记忆列表
        """
        candidate_indices = set(range(len(self.episodic_memories)))
        
        # 按技能领域筛选
        if skill_area and skill_area in self.episodic_index:
            candidate_indices &= set(self.episodic_index[skill_area])
        
        # 按标签筛选
        if tags:
            for tag in tags:
                tag_key = f"tag:{tag}"
                if tag_key in self.episodic_index:
                    candidate_indices &= set(self.episodic_index[tag_key])
        
        # 获取候选记忆
        candidates = [self.episodic_memories[i] for i in candidate_indices]
        
        # 按场景类型筛选
        if scenario_type:
            candidates = [m for m in candidates if m.scenario_type == scenario_type]
        
        # 只返回成功案例
        if only_successful:
            candidates = [m for m in candidates if m.is_successful]
        
        # 按时间排序（最近的优先）
        candidates.sort(key=lambda m: m.timestamp, reverse=True)
        
        return candidates[:limit]
    
    def extract_episodes_from_interview(self, interview_data: Dict) -> List[EpisodicMemory]:
        """
        从面试数据中提取关键情节
        
        Args:
            interview_data: 面试完整数据
            
        Returns:
            提取的情节记忆列表
        """
        episodes = []
        interview_id = interview_data.get("interview_id", "unknown")
        conversation_log = interview_data.get("conversation_log", [])
        
        # 提取问答对
        i = 0
        while i < len(conversation_log):
            entry = conversation_log[i]
            
            # 找到面试官的问题
            if entry.get("role") == "interviewer" and "content" in entry:
                question = entry["content"]
                question_category = entry.get("category", "未知")
                
                # 找到对应的候选人回答
                if i + 1 < len(conversation_log) and conversation_log[i + 1].get("role") == "candidate":
                    answer = conversation_log[i + 1]["content"]
                    
                    # 找到对应的评估（如果有）
                    evaluation = {}
                    if i + 2 < len(conversation_log) and conversation_log[i + 2].get("role") == "system":
                        eval_content = conversation_log[i + 2].get("content", "")
                        # 解析评分信息
                        evaluation = {"raw": eval_content}
                    
                    # 判断是否是值得记录的片段（有追问、评分异常等）
                    is_notable = (
                        entry.get("type") == "followup" or  # 追问问题
                        "追问" in str(evaluation.get("raw", "")) or
                        "露怯" in str(evaluation.get("raw", ""))
                    )
                    
                    if is_notable:
                        # 创建情节记忆
                        memory_id = f"{interview_id}_{i}"
                        episode = EpisodicMemory(
                            memory_id=memory_id,
                            interview_id=interview_id,
                            timestamp=datetime.now(),
                            scenario_type="followup" if entry.get("type") == "followup" else "normal",
                            question_category=question_category,
                            skill_area=question_category,  # 简化处理
                            question=question,
                            answer=answer,
                            evaluation=evaluation,
                            strategy_used="followup" if entry.get("type") == "followup" else "direct",
                            effectiveness=0.5,  # 默认效果
                            tags=["followup"] if entry.get("type") == "followup" else [],
                            is_successful="依然扎实" in str(evaluation.get("raw", "")),
                            is_failure="露怯" in str(evaluation.get("raw", ""))
                        )
                        episodes.append(episode)
            
            i += 1
        
        logger.info(f"📚 从面试中提取了 {len(episodes)} 个关键情节")
        return episodes
    
    # ==================== 语义记忆管理 ====================
    
    def add_semantic_memory(self, memory: SemanticMemory):
        """添加语义记忆"""
        self.semantic_memories[memory.memory_id] = memory
        logger.debug(f"🧩 添加语义记忆: {memory.pattern_name}")
    
    def get_semantic_memory(self, memory_id: str) -> Optional[SemanticMemory]:
        """获取特定语义记忆"""
        return self.semantic_memories.get(memory_id)
    
    def retrieve_semantic_patterns(
        self,
        knowledge_type: Optional[str] = None,
        min_confidence: float = 0.3,
        limit: int = 10
    ) -> List[SemanticMemory]:
        """
        检索语义模式
        
        Args:
            knowledge_type: 知识类型筛选
            min_confidence: 最小置信度
            limit: 返回数量限制
            
        Returns:
            相关的语义记忆列表
        """
        candidates = list(self.semantic_memories.values())
        
        # 按类型筛选
        if knowledge_type:
            candidates = [m for m in candidates if m.knowledge_type == knowledge_type]
        
        # 按置信度筛选
        candidates = [m for m in candidates if m.confidence >= min_confidence]
        
        # 按成功率排序
        candidates.sort(key=lambda m: (m.confidence, m.success_rate), reverse=True)
        
        return candidates[:limit]
    
    def update_semantic_from_episodes(self):
        """从情节记忆中提炼语义记忆"""
        # 分析追问策略的有效性
        followup_episodes = [e for e in self.episodic_memories if "followup" in e.tags]
        
        if len(followup_episodes) >= 5:  # 至少5个案例才提炼
            success_count = sum(1 for e in followup_episodes if e.is_successful)
            success_rate = success_count / len(followup_episodes)
            
            # 创建或更新语义记忆
            memory_id = "pattern_followup_effectiveness"
            if memory_id in self.semantic_memories:
                semantic = self.semantic_memories[memory_id]
                semantic.usage_count = len(followup_episodes)
                semantic.success_rate = success_rate
                semantic.confidence = min(1.0, len(followup_episodes) / 20.0)
                semantic.last_updated = datetime.now()
            else:
                semantic = SemanticMemory(
                    memory_id=memory_id,
                    knowledge_type="best_practice",
                    pattern_name="追问策略有效性",
                    pattern_description=f"追问策略在{len(followup_episodes)}次使用中，成功率为{success_rate:.2%}",
                    applicable_conditions=["候选人回答可疑", "评分偏高但缺乏细节"],
                    usage_count=len(followup_episodes),
                    success_rate=success_rate,
                    confidence=min(1.0, len(followup_episodes) / 20.0),
                    supporting_examples=[e.memory_id for e in followup_episodes[:10]]
                )
                self.add_semantic_memory(semantic)
            
            logger.info(f"✨ 更新语义记忆: 追问策略有效性 {success_rate:.2%}")
    
    # ==================== 持久化 ====================
    
    def save_memories(self):
        """保存记忆到磁盘"""
        try:
            # 保存情节记忆
            episodic_file = self.storage_dir / "episodic_memories.json"
            with open(episodic_file, 'w', encoding='utf-8') as f:
                data = [m.to_dict() for m in self.episodic_memories]
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 保存语义记忆
            semantic_file = self.storage_dir / "semantic_memories.json"
            with open(semantic_file, 'w', encoding='utf-8') as f:
                data = {k: v.to_dict() for k, v in self.semantic_memories.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 保存索引
            index_file = self.storage_dir / "episodic_index.pkl"
            with open(index_file, 'wb') as f:
                pickle.dump(dict(self.episodic_index), f)
            
            logger.success(f"💾 记忆已保存: {len(self.episodic_memories)} 条情节, "
                         f"{len(self.semantic_memories)} 条语义")
        except Exception as e:
            logger.error(f"❌ 保存记忆失败: {e}")
    
    def _load_memories(self):
        """从磁盘加载记忆"""
        try:
            # 加载情节记忆
            episodic_file = self.storage_dir / "episodic_memories.json"
            if episodic_file.exists():
                with open(episodic_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.episodic_memories = [EpisodicMemory.from_dict(m) for m in data]
            
            # 加载语义记忆
            semantic_file = self.storage_dir / "semantic_memories.json"
            if semantic_file.exists():
                with open(semantic_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.semantic_memories = {k: SemanticMemory.from_dict(v) for k, v in data.items()}
            
            # 加载索引
            index_file = self.storage_dir / "episodic_index.pkl"
            if index_file.exists():
                with open(index_file, 'rb') as f:
                    self.episodic_index = defaultdict(list, pickle.load(f))
            else:
                # 重建索引
                self._rebuild_index()
            
        except Exception as e:
            logger.warning(f"⚠️  加载记忆失败: {e}，使用空记忆")
    
    def _rebuild_index(self):
        """重建索引"""
        self.episodic_index.clear()
        for i, memory in enumerate(self.episodic_memories):
            self.episodic_index[memory.skill_area].append(i)
            for tag in memory.tags:
                self.episodic_index[f"tag:{tag}"].append(i)
        logger.info("🔄 重建记忆索引完成")
    
    # ==================== 记忆检索策略 ====================
    
    def retrieve_relevant_memories(
        self,
        context: Dict,
        memory_type: str = "episodic",
        limit: int = 5
    ) -> List[Any]:
        """
        智能检索相关记忆
        
        Args:
            context: 当前上下文（候选人画像、问题类型等）
            memory_type: 记忆类型 ("episodic" / "semantic")
            limit: 返回数量限制
            
        Returns:
            相关记忆列表
        """
        if memory_type == "episodic":
            # 从上下文提取检索条件
            skill_area = context.get("skill_area")
            scenario_type = context.get("scenario_type")
            tags = context.get("tags", [])
            
            return self.retrieve_episodic_memories(
                skill_area=skill_area,
                scenario_type=scenario_type,
                tags=tags,
                limit=limit,
                only_successful=context.get("only_successful", False)
            )
        
        elif memory_type == "semantic":
            knowledge_type = context.get("knowledge_type")
            min_confidence = context.get("min_confidence", 0.3)
            
            return self.retrieve_semantic_patterns(
                knowledge_type=knowledge_type,
                min_confidence=min_confidence,
                limit=limit
            )
        
        return []
