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
        
        # 先记录候选人的回答到对话历史
        self.conversation_history.append({
            "role": "candidate",
            "content": answer
        })
        
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
    
    def detect_shallow_answer(self, answer: str, target_skills: List[str], score: int) -> Dict[str, Any]:
        """
        检测回答是否浮于表面（可能是不懂装懂）
        
        Args:
            answer: 候选人回答
            target_skills: 目标技能列表
            score: 评分
            
        Returns:
            检测结果，包含是否可疑、可疑信号、建议追问的技能
        """
        signals = []
        suspicious = False
        
        # 信号1：使用高级术语但缺乏具体细节
        high_level_terms = ["微服务", "分布式", "高并发", "架构", "system design", 
                           "性能优化", "react", "hooks", "虚拟dom", "jvm", "spring"]
        has_high_level_term = any(term in answer.lower() for term in high_level_terms)
        
        # 信号2：使用模糊词汇
        vague_words = ["一般", "常用", "基本上", "差不多", "大概", "应该", "可能"]
        vague_count = sum(1 for word in vague_words if word in answer)
        
        # 信号3：回答太短（少于80字但得分高）
        answer_length = len(answer)
        is_too_short = answer_length < 80 and score >= 7
        
        # 信号4：没有数据/数字（对于技术问题很可疑）
        has_numbers = any(char.isdigit() for char in answer)
        
        # 信号5：没有具体例子或代码
        has_example = any(word in answer for word in ["例如", "比如", "举个例子", "具体", "代码"])
        
        # 综合判断
        if has_high_level_term and answer_length < 150:
            signals.append("使用高级术语但回答较短")
            suspicious = True
        
        if vague_count >= 2:
            signals.append(f"使用{vague_count}个模糊词汇")
            suspicious = True
        
        if is_too_short:
            signals.append(f"回答仅{answer_length}字但得分{score}分")
            suspicious = True
        
        if has_high_level_term and not has_numbers and score >= 7:
            signals.append("提到技术概念但无具体数据")
            suspicious = True
        
        if has_high_level_term and not has_example and answer_length < 100:
            signals.append("缺乏具体示例")
            suspicious = True
        
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
            "followup_skill": followup_skill,
            "answer_length": answer_length
        }
        
        if suspicious:
            logger.warning(f"⚠️  检测到可疑回答: {', '.join(signals)}")
        
        return result
    
    def generate_followup_question(self, skill: str, original_question: str, original_answer: str) -> str:
        """
        生成针对特定技能的追问问题
        
        Args:
            skill: 目标技能
            original_question: 原始问题
            original_answer: 原始回答
            
        Returns:
            追问问题
        """
        # 追问问题库（针对不同技能）
        followup_templates = {
            "system_design": [
                "你提到了{concept}，能具体说说这个方案能支持多大的并发量（QPS）吗？",
                "如果让你画个架构图来说明{concept}，你会怎么画？请描述主要模块和数据流。",
                "这个{concept}设计在实际项目中遇到过什么具体问题？是怎么解决的？",
                "能否说明一下{concept}方案的trade-off？为什么选择它而不是其他方案？"
            ],
            "微服务": [
                "你提到使用了{concept}，具体是用的什么中间件或框架？",
                "服务之间的数据一致性是如何保证的？能举个具体例子吗？",
                "如果一个服务挂了，整个系统会怎么处理？有什么降级策略？"
            ],
            "react": [
                "你提到React的{concept}，能写一小段代码示例来说明吗？",
                "React的{concept}底层原理是什么？和其他框架有什么本质区别？",
                "如果我问你virtual DOM的diff算法时间复杂度，你知道吗？",
                "在实际项目中使用{concept}时遇到过什么性能问题？"
            ],
            "java": [
                "你提到{concept}，能说说JVM的具体参数配置吗？",
                "Spring的{concept}源码你看过吗？能简单说说实现原理吗？",
                "在生产环境中{concept}的监控指标你会看哪些？"
            ],
            "performance": [
                "你提到性能优化，具体优化前后的指标是多少？",
                "这个优化方案的瓶颈分析是怎么做的？用了什么工具？",
                "如果数据量增长10倍，这个方案还能work吗？"
            ],
            "database": [
                "你提到数据库优化，能说说具体的索引设计吗？",
                "执行计划（EXPLAIN）结果你是怎么分析的？",
                "这个查询的时间复杂度是多少？数据量多大时会成为瓶颈？"
            ]
        }
        
        # 提取原始回答中的关键概念
        concepts = []
        keywords = ["微服务", "saga", "分布式", "hooks", "性能优化", "缓存", 
                   "消息队列", "架构", "jvm", "spring"]
        for keyword in keywords:
            if keyword in original_answer.lower():
                concepts.append(keyword)
        
        concept = concepts[0] if concepts else "这个方案"
        
        # 根据技能选择追问模板
        skill_lower = skill.lower()
        if "design" in skill_lower or "架构" in skill_lower:
            templates = followup_templates["system_design"]
        elif "react" in skill_lower or "前端" in skill_lower:
            templates = followup_templates["react"]
        elif "java" in skill_lower:
            templates = followup_templates["java"]
        elif "微服务" in skill_lower or "microservice" in skill_lower:
            templates = followup_templates["微服务"]
        elif "性能" in skill_lower or "performance" in skill_lower:
            templates = followup_templates["performance"]
        elif "数据库" in skill_lower or "sql" in skill_lower:
            templates = followup_templates["database"]
        else:
            # 默认通用追问
            templates = [
                "能举一个具体的代码示例或者项目案例来说明吗？",
                "如果遇到{concept}的边界情况或异常，你会怎么处理？",
                "这个{concept}的实现细节能展开说说吗？"
            ]
        
        # 随机选择一个模板
        import random
        template = random.choice(templates)
        question = template.format(concept=concept)
        
        logger.info(f"🔍 生成追问: {question}")
        return question
    
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
                formatted.append(f"\n【面试官提问】: {content}")
            elif role == "candidate":
                # 包含候选人的回答
                formatted.append(f"【候选人回答】: {content}")
            elif role == "interviewer" and entry_type == "evaluation":
                # 包含评估信息
                if isinstance(content, dict):
                    score = content.get("score", 0)
                    feedback = content.get("feedback", "")
                    formatted.append(f"  [评分: {score}/10 | 反馈: {feedback}]")
                else:
                    formatted.append(f"  [评分: {content}/10]")
        
        return "\n".join(formatted)
