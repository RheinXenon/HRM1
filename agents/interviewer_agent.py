"""
面试官Agent
负责生成面试问题、评估候选人回答、决策是否追问
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from loguru import logger

from agents.prompts.interviewer_prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    FOLLOW_UP_PROMPT,
    FINAL_REPORT_PROMPT
)


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
        self.all_evaluations = []  # 存储所有评估结果
        
    def generate_interview_script(self, candidate_level: str = "senior") -> List[InterviewQuestion]:
        """
        生成面试脚本（问题列表）
        
        Args:
            candidate_level: 候选人级别，用于调整问题难度
            
        Returns:
            面试问题列表
        """
        logger.info(f"正在生成{candidate_level}级别的面试问题...")
        
        questions = []
        categories = [
            ("职位相关", ["understanding", "motivation"]),
            ("技术能力", ["python", "system_design", "sql"]),
            ("行为面试", ["problem_solving", "teamwork"]),
            ("文化匹配", ["communication", "learning"])
        ]
        
        for category, skills in categories:
            try:
                category_questions = self._generate_questions_for_category(
                    category=category,
                    candidate_level=candidate_level,
                    expected_skills=skills
                )
                questions.extend(category_questions)
            except Exception as e:
                logger.warning(f"⚠️  生成{category}类问题失败: {e}, 使用默认问题")
                # 使用默认问题
                default_q = self._get_default_question(category, skills)
                questions.append(default_q)
        
        logger.success(f"✅ 生成{len(questions)}个面试问题")
        return questions
    
    def ask_question(self, question: InterviewQuestion) -> str:
        """
        提出面试问题
        
        Args:
            question: 问题对象
            
        Returns:
            格式化的问题文本
        """
        # 记录对话历史
        self.conversation_history.append({
            "role": "interviewer",
            "type": "question",
            "category": question.category,
            "content": question.question,
            "difficulty": question.difficulty,
            "expected_skills": question.expected_skills
        })
        
        return question.question
    
    def evaluate_answer(self, question: str, answer: str, target_skills: List[str] = None) -> Dict[str, Any]:
        """
        评估候选人回答
        
        Args:
            question: 问题内容
            answer: 候选人回答
            target_skills: 目标技能列表
            
        Returns:
            评估结果，包含分数和反馈
        """
        logger.info("正在评估候选人回答...")
        
        if target_skills is None:
            target_skills = []
        
        # 构建评估提示词
        system_prompt = self._build_system_prompt()
        user_message = ANSWER_EVALUATION_PROMPT.format(
            question=question,
            answer=answer,
            target_skills=", ".join(target_skills) if target_skills else "综合能力"
        )
        
        try:
            # 调用LLM进行评估
            evaluation_json = self.llm_client.chat_with_json_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )
            
            # 记录评估结果
            self.conversation_history.append({
                "role": "interviewer",
                "type": "evaluation",
                "content": evaluation_json
            })
            
            logger.success(f"✅ 评估完成: 分数 {evaluation_json.get('score', 0)}/10")
            return evaluation_json
            
        except Exception as e:
            logger.error(f"❌ 评估失败: {e}")
            # 返回默认评估
            return {
                "score": 5,
                "feedback": "评估失败，使用默认分数",
                "need_follow_up": "no"
            }
    
    def decide_follow_up(self, evaluation: Dict, original_question: str = None, answer: str = None) -> Optional[str]:
        """
        决策是否需要追问，并生成追问问题
        
        Args:
            evaluation: 上一次评估结果
            original_question: 原始问题
            answer: 候选人回答
            
        Returns:
            追问问题，如果不需要追问则返回None
        """
        # 检查是否需要追问
        need_follow_up = evaluation.get("need_follow_up", "no").lower()
        
        if need_follow_up != "yes":
            return None
        
        # Phase 1: 简化版，不进行复杂追问
        # Phase 2 可以添加更智能的追问逻辑
        logger.info("评估结果显示需要追问，但Phase 1版本暂不实现追问")
        return None
    
    def generate_final_report(self, candidate_name: str) -> Dict[str, Any]:
        """
        生成最终评估报告
        
        Args:
            candidate_name: 候选人姓名
            
        Returns:
            完整的评估报告
        """
        logger.info("正在生成最终评估报告...")
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt()
        
        # 格式化对话记录
        conversation_summary = self._format_conversation_log()
        
        # 构建报告生成提示词
        user_message = FINAL_REPORT_PROMPT.format(
            candidate_name=candidate_name,
            job_title=self.job_config.get("title", "未知职位"),
            conversation_log=conversation_summary,
            job_requirements=json.dumps(self.job_config.get("requirements", {}), ensure_ascii=False, indent=2)
        )
        
        try:
            # 调用LLM生成报告
            report = self.llm_client.chat_with_json_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )
            
            logger.success("✅ 最终报告生成成功")
            return report
            
        except Exception as e:
            logger.error(f"❌ 报告生成失败: {e}")
            # 返回默认报告
            return {
                "error": "报告生成失败",
                "recommendation_score": 50,
                "recommendation": "未能生成评估"
            }
    
    def _build_system_prompt(self) -> str:
        """
        构建系统提示词
        
        Returns:
            完整的系统提示词
        """
        company_info = f"""
公司名称: {self.company_config.get('name', '')}
行业: {self.company_config.get('industry', '')}
公司规模: {self.company_config.get('size', '')}
公司描述: {self.company_config.get('description', '')}
"""
        
        job_requirements = f"""
职位名称: {self.job_config.get('title', '')}
职位描述: {self.job_config.get('description', '')}
核心要求: {json.dumps(self.job_config.get('requirements', {}), ensure_ascii=False, indent=2)}
"""
        
        system_prompt = INTERVIEWER_SYSTEM_PROMPT.format(
            company_name=self.company_config.get('name', ''),
            job_title=self.job_config.get('title', ''),
            company_info=company_info,
            job_requirements=job_requirements
        )
        
        return system_prompt
    
    def _generate_questions_for_category(
        self,
        category: str,
        candidate_level: str,
        expected_skills: List[str]
    ) -> List[InterviewQuestion]:
        """
        为特定类别生成问题
        
        Args:
            category: 问题类别
            candidate_level: 候选人级别
            expected_skills: 期望考察的技能
            
        Returns:
            问题列表
        """
        system_prompt = self._build_system_prompt()
        user_message = QUESTION_GENERATION_PROMPT.format(
            job_title=self.job_config.get("title", ""),
            candidate_level=candidate_level,
            question_category=category
        )
        
        # 调用LLM生成问题
        result = self.llm_client.chat_with_json_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        
        # 解析问题
        questions = []
        question_list = result.get("questions", [])
        
        for q in question_list:
            if isinstance(q, dict):
                questions.append(InterviewQuestion(
                    category=category,
                    question=q.get("question", ""),
                    difficulty=q.get("difficulty", 5),
                    expected_skills=expected_skills
                ))
            elif isinstance(q, str):
                questions.append(InterviewQuestion(
                    category=category,
                    question=q,
                    difficulty=5,
                    expected_skills=expected_skills
                ))
        
        return questions[:2]  # Phase 1: 每个类别只取2个问题
    
    def _get_default_question(self, category: str, skills: List[str]) -> InterviewQuestion:
        """
        获取默认问题
        
        Args:
            category: 问题类别
            skills: 目标技能
            
        Returns:
            默认问题
        """
        default_questions = {
            "职位相关": "请介绍一下你为什么对这个职位感兴趣？",
            "技术能力": "请讲述一下你最引以为傲的技术项目经验。",
            "行为面试": "请描述一次你面对挑战时的经历，你是如何解决的？",
            "文化匹配": "你如何看待团队协作和沟通？"
        }
        
        return InterviewQuestion(
            category=category,
            question=default_questions.get(category, "请分享你的经验。"),
            difficulty=5,
            expected_skills=skills
        )
    
    def _format_conversation_log(self) -> str:
        """
        格式化对话记录用于报告生成
        
        Returns:
            格式化的对话字符串
        """
        formatted = []
        
        for entry in self.conversation_history:
            role = entry.get("role", "")
            entry_type = entry.get("type", "")
            content = entry.get("content", "")
            
            if role == "interviewer" and entry_type == "question":
                formatted.append(f"\n面试官: {content}")
            elif role == "interviewer" and entry_type == "evaluation":
                score = content.get("score", 0) if isinstance(content, dict) else 0
                formatted.append(f"  [评分: {score}/10]")
        
        return "\n".join(formatted)
