"""
面试官Agent
负责生成面试问题、评估候选人回答、决策是否追问
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class InterviewQuestion:
    """面试问题数据类"""
    category: str  # 问题类别：职位/技术/文化/行为
    question: str  # 问题内容
    difficulty: int  # 难度等级 1-10
    expected_skills: List[str]  # 期望考察的技能


class InterviewerAgent:
    """面试官Agent类"""
    
    def __init__(self, llm_client, job_config: Dict, company_config: Dict):
        """
        初始化面试官Agent
        
        Args:
            llm_client: LLM客户端实例
            job_config: 职位配置
            company_config: 公司信息配置
        """
        self.llm_client = llm_client
        self.job_config = job_config
        self.company_config = company_config
        self.conversation_history = []
        
    def generate_interview_script(self, candidate_level: str = "senior") -> List[InterviewQuestion]:
        """
        生成面试脚本（问题列表）
        
        Args:
            candidate_level: 候选人级别，用于调整问题难度
            
        Returns:
            面试问题列表
        """
        # TODO: 实现问题生成逻辑
        pass
    
    def ask_question(self, question: InterviewQuestion) -> str:
        """
        提出面试问题
        
        Args:
            question: 问题对象
            
        Returns:
            格式化的问题文本
        """
        # TODO: 实现提问逻辑
        pass
    
    def evaluate_answer(self, question: str, answer: str) -> Dict[str, Any]:
        """
        评估候选人回答
        
        Args:
            question: 问题内容
            answer: 候选人回答
            
        Returns:
            评估结果，包含分数和反馈
        """
        # TODO: 实现评估逻辑
        pass
    
    def decide_follow_up(self, evaluation: Dict) -> Optional[str]:
        """
        决策是否需要追问，并生成追问问题
        
        Args:
            evaluation: 上一次评估结果
            
        Returns:
            追问问题，如果不需要追问则返回None
        """
        # TODO: 实现追问决策逻辑
        pass
    
    def generate_final_report(self) -> Dict[str, Any]:
        """
        生成最终评估报告
        
        Returns:
            完整的评估报告
        """
        # TODO: 实现报告生成逻辑
        pass
