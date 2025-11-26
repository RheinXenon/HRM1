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
from core.score_normalizer import ScoreNormalizer
from domains import DomainLoader


@dataclass
class InterviewQuestion:
    """面试问题数据类"""
    category: str  # 问题类别：职位/技术/文化/行为
    question: str  # 问题内容
    difficulty: int  # 难度等级 1-10 (注：评分系统已升级为0-100标准化分数，但问题难度仍用1-10便于配置)
    expected_skills: List[str]  # 期望考察的技能


class InterviewerAgent:
    """面试官Agent类"""
    
    def __init__(self, llm_client, job_config: Dict, company_config: Dict, domain_id: str = "tech"):
        """
        初始化面试官Agent

        Args:
            llm_client: LLM客户端实例
            job_config: 职位配置
            company_config: 公司信息配置
            domain_id: 领域ID（tech/marketing/healthcare等），默认为tech
        """
        self.llm_client = llm_client
        self.job_config = job_config
        self.company_config = company_config
        self.conversation_history = []
        self.all_evaluations = []  # 存储所有评估结果

        # Phase 1: 初始化评分标准化器
        self.score_normalizer = ScoreNormalizer()
        logger.info("✅ 评分标准化器已加载")
        
        # 加载领域配置
        self.domain = DomainLoader(domain_id)
        logger.info(f"✅ 领域配置已加载: {self.domain.domain_id}")
        
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
        
        # 从候选人配置中获取技能列表，动态生成问题类别
        candidate_skills = list(candidate_profile.get("skills", {}).keys())
        
        # 将技能分为核心技能和软技能
        soft_skills = ["communication", "teamwork", "problem_solving", "learning", "leadership"]
        core_skills = [s for s in candidate_skills if s not in soft_skills][:6]  # 最多6个核心技能
        
        categories = [
            ("职位相关", ["understanding", "motivation"]),
            ("专业能力", core_skills if core_skills else candidate_skills[:3]),
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
        评估候选人回答 (Phase 1: 多维度评分 + 标准化)

        Args:
            question: 问题内容
            answer: 候选人回答
            target_skills: 目标技能列表

        Returns:
            评估结果，包含维度评分、标准化分数和反馈
        """
        logger.info("正在评估候选人回答 (多维度评分)...")

        # 先记录候选人的回答到对话历史
        self.conversation_history.append({
            "role": "candidate",
            "content": answer
        })

        if target_skills is None:
            target_skills = []

        # 构建评估提示词（动态传入domain信号词）
        system_prompt = self._build_system_prompt()
        
        # 从domain获取信号词示例
        high_level_terms = self.domain.get_high_level_terms()
        technical_metrics = self.domain.get_technical_metrics()
        
        # 构建提示语
        high_level_hint = f"（如{', '.join(high_level_terms[:3])}等）" if high_level_terms else ""
        metrics_hint = f"（如{', '.join(technical_metrics[:3])}等）" if technical_metrics else ""
        
        user_message = ANSWER_EVALUATION_PROMPT.format(
            question=question,
            answer=answer,
            target_skills=", ".join(target_skills) if target_skills else "综合能力",
            high_level_terms_hint=high_level_hint,
            metrics_hint=metrics_hint
        )

        try:
            # 调用LLM进行多维度评估
            evaluation_json = self.llm_client.chat_with_json_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )

            # 验证和标准化维度评分
            dimension_scores = evaluation_json.get("dimension_scores", {})

            # 如果缺少维度评分，使用默认值
            if not dimension_scores:
                logger.warning("⚠️  LLM未返回dimension_scores，使用默认值")
                dimension_scores = {
                    "technical_depth": 2,
                    "practical_experience": 2,
                    "answer_specificity": 2,
                    "logical_clarity": 2,
                    "honesty": 3,
                    "communication": 2
                }

            # 验证维度评分
            if not self.score_normalizer.validate_dimension_scores(dimension_scores):
                logger.warning("⚠️  维度评分验证失败，使用默认值")
                dimension_scores = {
                    "technical_depth": 2,
                    "practical_experience": 2,
                    "answer_specificity": 2,
                    "logical_clarity": 2,
                    "honesty": 3,
                    "communication": 2
                }

            # 使用标准化器计算标准化分数
            normalized_score = self.score_normalizer.normalize_dimension_scores(dimension_scores)

            # 获取分数解释
            score_interpretation = self.score_normalizer.get_score_interpretation(normalized_score)

            # 整合评估结果
            evaluation_result = {
                # Phase 1: 新增字段
                "dimension_scores": dimension_scores,
                "normalized_score": normalized_score,
                "score_interpretation": score_interpretation,

                # 兼容旧字段 (用于其他模块)
                "score": int(normalized_score / 10),  # 转换为1-10分，兼容旧代码

                # LLM原始输出
                "feedback": evaluation_json.get("feedback", ""),
                "confidence_level": evaluation_json.get("confidence_level", "uncertain"),
                "need_follow_up": evaluation_json.get("need_follow_up", "no"),
                "follow_up_direction": evaluation_json.get("follow_up_direction", "")
            }

            # 记录评估结果
            self.conversation_history.append({
                "role": "interviewer",
                "type": "evaluation",
                "content": evaluation_result
            })

            logger.success(
                f"✅ 评估完成: 标准化分数 {normalized_score:.1f}/100 "
                f"({score_interpretation['recommendation']})"
            )

            return evaluation_result

        except Exception as e:
            logger.error(f"❌ 评估失败: {e}")
            import traceback
            traceback.print_exc()

            # 返回默认评估
            return {
                "dimension_scores": {
                    "technical_depth": 2,
                    "practical_experience": 2,
                    "answer_specificity": 2,
                    "logical_clarity": 2,
                    "honesty": 3,
                    "communication": 2
                },
                "normalized_score": 50.0,
                "score": 5,
                "feedback": "评估失败，使用默认分数",
                "need_follow_up": "no"
            }
    
    def detect_shallow_answer(self, answer: str, target_skills: List[str], score: int) -> Dict[str, Any]:
        """
        检测回答是否浮于表面（可能是不懂装懂）
        
        Args:
            answer: 候选人回答
            target_skills: 目标技能列表
            score: 评分（注意：此处使用1-10分制的兼容格式，非0-100标准化分数）
            
        Returns:
            检测结果，包含是否可疑、可疑信号、建议追问的技能
        """
        signals = []
        suspicious = False
        suspicion_score = 0  # 可疑程度评分，用于更精准的判断
        
        # 从领域配置加载信号词汇
        high_level_terms = self.domain.get_high_level_terms()
        vague_words = self.domain.get_vague_words()
        weakness_indicators = self.domain.get_weakness_indicators()
        
        # 信号1：使用高级术语但缺乏具体细节
        has_high_level_term = any(term in answer.lower() for term in high_level_terms)
        high_level_count = sum(1 for term in high_level_terms if term in answer.lower())
        
        # 信号2：使用模糊词汇
        vague_count = sum(1 for word in vague_words if word in answer)
        
        # 信号3：露怯关键词
        has_weakness = any(phrase in answer for phrase in weakness_indicators)
        
        # 信号4：回答长度分析
        answer_length = len(answer)
        is_too_short = answer_length < 100 and score >= 7
        is_very_short = answer_length < 60 and score >= 6
        
        # 信号5：缺少具体内容
        concrete_evidence = self.domain.get_concrete_evidence()
        technical_metrics = self.domain.get_technical_metrics()
        
        has_numbers = any(char.isdigit() for char in answer)
        has_example = any(word in answer for word in concrete_evidence)
        has_metrics = any(word in answer for word in technical_metrics)
        
        # 信号6：空话套话
        empty_phrases = self.domain.get_empty_phrases()
        empty_count = sum(1 for phrase in empty_phrases if phrase in answer)
        
        # === 综合判断逻辑（改进版）===
        
        # 1. 高级术语但缺乏深度（强信号）
        if has_high_level_term and answer_length < 200:
            if not has_numbers and not has_example:
                signals.append("使用高级术语但缺乏具体细节")
                suspicion_score += 3
        
        # 2. 多个高级术语但回答很短（强信号）
        if high_level_count >= 3 and answer_length < 150:
            signals.append(f"提到{high_level_count}个技术概念但回答过短")
            suspicion_score += 2
        
        # 3. 模糊词汇过多（中等信号）
        if vague_count >= 3:
            signals.append(f"使用{vague_count}个不确定词汇")
            suspicion_score += 2
        elif vague_count >= 2 and answer_length < 150:
            signals.append(f"回答短且使用{vague_count}个模糊词")
            suspicion_score += 1
        
        # 4. 回答过短但得分高（强信号）
        if is_very_short:
            signals.append(f"回答仅{answer_length}字但得分{score}分")
            suspicion_score += 3
        elif is_too_short:
            signals.append(f"回答较短（{answer_length}字）")
            suspicion_score += 1
        
        # 5. 提到技术但无具体数据（中等信号）
        if has_high_level_term and not has_numbers and not has_metrics and score >= 7:
            signals.append("提到技术概念但缺少量化指标")
            suspicion_score += 2
        
        # 6. 缺乏具体示例（中等信号）
        if has_high_level_term and not has_example and answer_length < 150:
            signals.append("缺乏具体示例或代码说明")
            suspicion_score += 2
        
        # 7. 明确承认不熟悉（强信号）
        if has_weakness:
            if score >= 6:
                signals.append("承认知识有限但仍给出回答")
                suspicion_score += 3
            else:
                signals.append("承认对该领域不够熟悉")
                suspicion_score += 1
        
        # 8. 空话套话多（轻信号）
        if empty_count >= 3 and answer_length < 200:
            signals.append("包含较多空话套话")
            suspicion_score += 1
        
        # 最终判断：降低阈值，suspicion_score >= 3 认为可疑（提高追问触发率）
        suspicious = suspicion_score >= 3
        
        # 确定建议追问的技能
        followup_skill = None
        if suspicious and target_skills:
            # 找出回答中提到的技能
            for skill in target_skills:
                if skill.lower() in answer.lower():
                    followup_skill = skill
                    break
            if not followup_skill:
                followup_skill = target_skills[0] if target_skills else None
        
        result = {
            "is_suspicious": suspicious,
            "signals": signals,
            "signal_count": len(signals),
            "suspicion_score": suspicion_score,
            "followup_skill": followup_skill,
            "answer_length": answer_length,
            "has_weakness_indicator": has_weakness
        }
        
        if suspicious:
            logger.warning(f"⚠️  检测到可疑回答 (可疑度{suspicion_score}): {', '.join(signals)}")
        
        return result
    
    def generate_followup_question(
        self, 
        skill: str, 
        original_question: str, 
        original_answer: str, 
        evaluation: Dict = None
    ) -> str:
        """
        使用LLM智能生成针对特定技能的追问问题
        
        Args:
            skill: 目标技能
            original_question: 原始问题
            original_answer: 原始回答
            evaluation: 评估结果（可选）
            
        Returns:
            追问问题
        """
        logger.info(f"🔍 正在生成针对'{skill}'的智能追问...")
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt()
        
        # 准备评估反馈
        eval_feedback = ""
        if evaluation:
            eval_feedback = f"评分: {evaluation.get('score', 0)}/10\n"
            eval_feedback += f"反馈: {evaluation.get('feedback', '')}\n"
            eval_feedback += f"信心水平: {evaluation.get('confidence_level', 'unknown')}\n"
            eval_feedback += f"追问方向: {evaluation.get('follow_up_direction', '')}"
        else:
            eval_feedback = "候选人回答似乎缺乏深度，需要验证真实能力"
        
        # 使用FOLLOW_UP_PROMPT生成追问
        user_message = FOLLOW_UP_PROMPT.format(
            original_question=original_question,
            answer=original_answer,
            evaluation=eval_feedback,
            target_skill=skill
        )
        
        try:
            # 调用LLM生成追问问题
            followup_question = self.llm_client.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7  # 适度创造性
            )
            
            # 清理可能的多余内容
            followup_question = followup_question.strip()
            # 如果LLM返回了解释性文字，只保留问题部分
            if '\n' in followup_question:
                # 取第一个问句
                lines = [line.strip() for line in followup_question.split('\n') if line.strip()]
                for line in lines:
                    if '?' in line or '？' in line or line.endswith('吗') or line.endswith('呢'):
                        followup_question = line
                        break
                else:
                    followup_question = lines[0] if lines else followup_question
            
            logger.success(f"✅ 智能追问生成: {followup_question[:50]}...")
            return followup_question
            
        except Exception as e:
            logger.error(f"❌ LLM追问生成失败: {e}，使用备用模板")
            # 降级到简单模板
            return self._generate_fallback_followup(skill, original_answer)
    
    def _generate_fallback_followup(self, skill: str, original_answer: str) -> str:
        """
        生成备用追问问题（当LLM失败时使用）
        
        Args:
            skill: 目标技能
            original_answer: 原始回答
            
        Returns:
            备用追问问题
        """
        # 提取回答中的技术概念
        tech_terms = []
        keywords = ["微服务", "分布式", "架构", "性能", "优化", "缓存", 
                   "数据库", "算法", "框架", "设计模式"]
        for keyword in keywords:
            if keyword in original_answer:
                tech_terms.append(keyword)
        
        concept = tech_terms[0] if tech_terms else skill
        
        # 简单但有效的追问模板
        fallback_questions = [
            f"你提到了{concept}，能具体说说实际项目中的应用场景和遇到的问题吗？",
            f"关于{concept}，能展开讲讲具体的技术细节或实现方案吗？",
            f"在使用{concept}时，你是如何保证性能和稳定性的？有具体的指标吗？"
        ]
        
        import random
        return random.choice(fallback_questions)
    
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
        
        # Phase 2: 实现智能追问（已启用）
        logger.info("评估结果显示需要追问，准备生成追问问题...")
        return None  # 注意：实际追问在interview_engine中处理
    
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
                formatted.append(f"\n【面试官提问】: {content}")
            elif role == "candidate":
                # 包含候选人的回答
                formatted.append(f"【候选人回答】: {content}")
            elif role == "interviewer" and entry_type == "evaluation":
                # 包含评估信息 (Phase 1: 使用标准化评分)
                if isinstance(content, dict):
                    # 优先使用新的标准化评分
                    normalized_score = content.get("normalized_score", None)
                    if normalized_score is not None:
                        score_interp = content.get("score_interpretation", {})
                        recommendation = score_interp.get("recommendation", "")
                        feedback = content.get("feedback", "")
                        formatted.append(f"  [评分: {normalized_score:.1f}/100 ({recommendation}) | 反馈: {feedback}]")
                    else:
                        # 降级到旧评分格式
                        score = content.get("score", 0)
                        feedback = content.get("feedback", "")
                        formatted.append(f"  [评分: {score}/10 | 反馈: {feedback}]")
                else:
                    formatted.append(f"  [评分: {content}]")
        
        return "\n".join(formatted)
