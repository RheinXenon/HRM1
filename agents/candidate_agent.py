"""
候选人Agent
基于配置的能力画像和性格特质，自主生成面试回答
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import json
from loguru import logger

from agents.prompts.candidate_prompts import (
    CANDIDATE_SYSTEM_PROMPT,
    SELF_INTRODUCTION_PROMPT,
    ANSWER_GENERATION_PROMPT,
    CANDIDATE_QUESTION_PROMPT,
    get_skill_description,
    format_personality_traits
)


@dataclass
class CandidateProfile:
    """候选人配置数据类"""
    name: str
    skills: Dict[str, int]  # 技能名称 -> 等级(1-10, 配置便利性, 评分系统内部使用0-100标准化分数)
    experience: Dict[str, Any]  # 经验信息
    personality: Dict[str, int]  # 性格特质参数
    knowledge_blind_spots: Dict[str, list] = None  # 知识盲区


class CandidateAgent:
    """候选人Agent类"""
    
    def __init__(self, llm_client, profile: CandidateProfile):
        """
        初始化候选人Agent
        
        Args:
            llm_client: LLM客户端实例
            profile: 候选人配置
        """
        self.llm_client = llm_client
        self.profile = profile
        self.conversation_history = []
        
    def introduce_self(self) -> str:
        """
        生成自我介绍
        
        Returns:
            自我介绍文本
        """
        logger.info(f"候选人 {self.profile.name} 正在生成自我介绍...")
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt()
        
        try:
            # 调用LLM生成自我介绍
            introduction = self.llm_client.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=SELF_INTRODUCTION_PROMPT,
                temperature=0.8
            )
            
            # 记录对话历史
            self.conversation_history.append({
                "role": "candidate",
                "type": "introduction",
                "content": introduction
            })
            
            logger.success(f"✅ 自我介绍生成成功")
            return introduction.strip()
            
        except Exception as e:
            logger.error(f"❌ 自我介绍生成失败: {e}")
            raise
    
    def answer_question(self, question: str, question_context: Dict = None) -> str:
        """
        根据问题生成回答
        
        Args:
            question: 面试问题
            question_context: 问题上下文（类别、难度等）
            
        Returns:
            候选人回答
        """
        logger.info(f"候选人正在回答问题...")
        
        if question_context is None:
            question_context = {}
        
        # 获取问题相关信息
        question_category = question_context.get("category", "未知")
        related_skills = question_context.get("expected_skills", [])
        is_followup = question_context.get("is_followup", False)
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt()
        
        # 构建用户消息
        user_message = ANSWER_GENERATION_PROMPT.format(
            question=question,
            question_category=question_category,
            related_skills=", ".join(related_skills) if related_skills else "综合能力"
        )
        
        # 如果是追问，使用思维链强制自我评估
        if is_followup:
            # 获取相关技能的actual_level
            skill_levels = {}
            for skill in related_skills:
                skill_levels[skill] = self.profile.skills.get(skill, 0)
            
            # 构建禁用术语列表（基于技能等级）
            forbidden_terms = self._get_forbidden_terms(related_skills, skill_levels)
            
            user_message += "\n\n🚨 **这是追问！必须先进行自我能力评估！** 🚨\n\n"
            user_message += "**第一步：自我评估（在心里思考，不要说出来）**\n"
            
            for skill, level in skill_levels.items():
                user_message += f"\n关于 {skill} (actual_level={level}/10):\n"
                if level <= 3:
                    user_message += "- 我的真实水平：只听说过，没实际用过\n"
                    user_message += "- 我知道的词汇：" + ", ".join(["基本概念", "技术名称"]) + "\n"
                    user_message += "- ❌ 我绝对不知道的：任何API、配置参数、工作原理、内部机制\n"
                elif level <= 5:
                    user_message += "- 我的真实水平：用过基础功能，但不深入\n"
                    user_message += "- 我知道的词汇：基本使用方法、常见场景\n"
                    user_message += "- ❌ 我绝对不知道的：具体配置参数、深层原理、性能优化细节\n"
                else:
                    user_message += "- 我的真实水平：熟练使用，了解原理\n"
                    user_message += "- 我知道的：基本原理和常用配置\n"
            
            if forbidden_terms:
                user_message += "\n⛔ **禁止使用的术语（你不可能知道这些词）：**\n"
                user_message += "```\n" + ", ".join(forbidden_terms[:20]) + "\n```\n"
                user_message += "如果你的回答中包含任何这些词，说明你在'圆过去'！\n"
            
            user_message += "\n**第二步：基于评估结果回答**\n"
            user_message += "- 只使用你'知道的词汇'列表中的内容\n"
            user_message += "- 不要使用'禁止使用的术语'\n"
            user_message += "- 如果答不上来，直接说'这个我不太清楚'\n"
            user_message += "- 可以给出错误的理解（符合你的低能力等级）\n"
            user_message += "\n**记住：追问不会让你'突然想起来'高级知识！**\n"
        
        try:
            # 构建完整的对话历史
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加之前的对话历史（最近5轮，避免上下文过长）
            recent_history = self.conversation_history[-10:]  # 5轮=10条消息
            for entry in recent_history:
                if entry.get("type") == "question":
                    messages.append({
                        "role": "user",
                        "content": f"[面试官提问] {entry['content']}"
                    })
                elif entry.get("type") == "answer":
                    messages.append({
                        "role": "assistant",
                        "content": entry['content']
                    })
            
            # 添加当前问题
            messages.append({"role": "user", "content": user_message})
            
            # 调用LLM生成回答（使用完整对话历史）
            response = self.llm_client.chat_completion(
                messages=messages,
                temperature=0.7
            )
            
            answer = response.strip()
            
            # 如果是追问，进行后处理过滤
            if is_followup and related_skills:
                answer = self._post_process_followup_answer(
                    answer, 
                    related_skills,
                    skill_levels if 'skill_levels' in locals() else {}
                )
            
            # 记录对话历史
            self.conversation_history.append({
                "role": "candidate",
                "type": "answer",
                "content": answer,
                "question": question
            })
            
            logger.success(f"✅ 回答生成成功 (上下文: {len(messages)}条消息)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ 回答生成失败: {e}")
            raise
    
    def ask_question_to_interviewer(self) -> str:
        """
        候选人向面试官提问
        
        Returns:
            候选人的问题
        """
        logger.info(f"候选人正在准备提问...")
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt()
        
        try:
            # 调用LLM生成问题
            questions = self.llm_client.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=CANDIDATE_QUESTION_PROMPT,
                temperature=0.8
            )
            
            # 记录对话历史
            self.conversation_history.append({
                "role": "candidate",
                "type": "question_to_interviewer",
                "content": questions
            })
            
            logger.success(f"✅ 候选人问题生成成功")
            return questions.strip()
            
        except Exception as e:
            logger.error(f"❌ 候选人提问生成失败: {e}")
            raise
    
    def _get_skill_level(self, skill_name: str) -> int:
        """
        获取某项技能的等级
        
        Args:
            skill_name: 技能名称
            
        Returns:
            技能等级，如果不存在则返回0
        """
        return self.profile.skills.get(skill_name, 0)
    
    def _get_forbidden_terms(self, skills: list, skill_levels: dict) -> list:
        """
        根据技能等级生成禁用术语列表
        
        Args:
            skills: 技能列表
            skill_levels: 技能等级字典
            
        Returns:
            禁用术语列表
        """
        forbidden_terms = []
        
        # 通用高级术语库（level <= 5 都不应该知道）
        advanced_terms = {
            "react": [
                "依赖数组", "dependency array", "浅比较", "shallow compare",
                "Object.is", "useCallback", "useMemo", "useRef",
                "cleanup", "清理函数", "闭包陷阱", "stale closure",
                "reconciliation", "fiber", "concurrent mode", "suspense",
                "批量更新", "批处理", "优先级调度"
            ],
            "rabbitmq": [
                "publisher confirm", "mandatory", "durable", "persistent",
                "disk flush", "镜像队列", "仲裁队列", "lazy queue",
                "federation", "shovel", "prefetch", "ACK模式",
                "消息持久化策略", "刷盘策略"
            ],
            "redis": [
                "AOF重写", "RDB快照", "混合持久化", "主从复制",
                "哨兵", "cluster", "gossip协议", "槽位",
                "pipeline", "事务", "lua脚本", "pub/sub"
            ],
            "java": [
                "JVM调优", "GC算法", "内存模型", "happens-before",
                "volatile", "synchronized", "CAS", "AQS",
                "线程池参数", "类加载机制", "双亲委派"
            ],
            "python": [
                "GIL", "装饰器原理", "元类", "描述符",
                "上下文管理器", "生成器表达式", "协程",
                "asyncio事件循环", "内存管理机制"
            ],
            "sql": [
                "执行计划", "索引覆盖", "回表", "最左前缀",
                "MVCC", "隔离级别", "间隙锁", "死锁检测",
                "查询优化器", "统计信息"
            ],
            "kubernetes": [
                "etcd", "控制器模式", "operator", "CRD",
                "亲和性", "污点", "容忍度", "HPA",
                "存储类", "CNI", "CSI", "调度器"
            ],
            "system_design": [
                "CAP定理", "BASE理论", "Paxos", "Raft",
                "一致性哈希", "布隆过滤器", "限流算法",
                "降级熔断", "分布式事务", "补偿机制"
            ]
        }
        
        # 基础术语库（level <= 3 也不应该知道）
        basic_terms = {
            "react": [
                "组件生命周期", "状态管理", "props传递", "事件处理",
                "条件渲染", "列表渲染", "表单处理"
            ],
            "rabbitmq": [
                "交换机", "队列", "绑定", "路由键",
                "消费者", "生产者", "虚拟主机"
            ],
            "redis": [
                "字符串", "列表", "哈希", "集合", "有序集合",
                "过期时间", "缓存穿透", "缓存雪崩"
            ]
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            level = skill_levels.get(skill, 0)
            
            # level <= 3: 连基础术语都不应该知道细节
            if level <= 3:
                if skill_lower in advanced_terms:
                    forbidden_terms.extend(advanced_terms[skill_lower])
                if skill_lower in basic_terms:
                    # level 3 对基础术语只能"听说过"，不能深入解释
                    forbidden_terms.extend(basic_terms[skill_lower])
            
            # level 4-5: 不应该知道高级术语
            elif level <= 5:
                if skill_lower in advanced_terms:
                    forbidden_terms.extend(advanced_terms[skill_lower])
        
        return list(set(forbidden_terms))  # 去重
    
    def _post_process_followup_answer(self, answer: str, skills: list, skill_levels: dict) -> str:
        """
        对追问回答进行后处理，替换禁用术语
        
        Args:
            answer: 原始回答
            skills: 技能列表
            skill_levels: 技能等级字典
            
        Returns:
            处理后的回答
        """
        forbidden_terms = self._get_forbidden_terms(skills, skill_levels)
        
        # 替换策略：将禁用术语替换为模糊表达
        replacements = {
            # React相关
            "依赖数组": "那个...数组配置",
            "dependency array": "那个数组参数",
            "浅比较": "对比机制",
            "shallow compare": "比较方式",
            "useCallback": "某个hooks",
            "useMemo": "某个优化方法",
            "useRef": "某个hooks",
            "cleanup": "清理的东西",
            "清理函数": "清理的那部分",
            "Object.is": "对比方法",
            "闭包陷阱": "闭包的问题",
            
            # RabbitMQ相关
            "publisher confirm": "发送确认机制",
            "durable": "持久化配置",
            "persistent": "持久化",
            "mandatory": "某个参数",
            "ACK模式": "确认模式",
            
            # 通用替换
            "配置参数": "配置",
            "具体配置": "一些配置",
        }
        
        modified_answer = answer
        found_terms = []
        
        for term in forbidden_terms:
            if term.lower() in modified_answer.lower():
                found_terms.append(term)
                # 使用替换表或通用模糊化
                replacement = replacements.get(term, "那个...我忘了叫什么")
                # 大小写不敏感替换
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                modified_answer = pattern.sub(replacement, modified_answer)
        
        if found_terms:
            logger.warning(f"⚠️  检测到并替换了禁用术语: {', '.join(found_terms[:5])}")
            # 在回答末尾添加不确定性表达
            if "这块" not in modified_answer and "说实话" not in modified_answer:
                modified_answer += " 说实话这块我理解得不够深入。"
        
        return modified_answer
    
    def _build_system_prompt(self) -> str:
        """
        构建系统提示词
        
        Returns:
            完整的系统提示词
        """
        # 格式化技能描述
        skill_profile = "\n".join([
            get_skill_description(skill, level)
            for skill, level in self.profile.skills.items()
        ])
        
        # 格式化工作经历
        exp = self.profile.experience
        work_experience = f"""
工作年限: {exp.get('years', 0)}年
职位级别: {exp.get('level', '未知')}
项目经历: {len(exp.get('projects', []))}个项目
"""
        
        # 如果有详细项目信息
        if 'projects' in exp and isinstance(exp['projects'], list) and len(exp['projects']) > 0:
            if isinstance(exp['projects'][0], dict):
                work_experience += "\n主要项目:\n"
                for i, proj in enumerate(exp['projects'][:3], 1):  # 最多显示3个
                    work_experience += f"{i}. {proj.get('name', '项目')}: {proj.get('role', '开发者')} - {proj.get('achievement', '完成项目开发')}\n"
        
        # 格式化性格特质
        personality_traits = format_personality_traits(self.profile.personality)
        
        # 获取性格参数用于模板
        personality = self.profile.personality
        comm = personality.get("communication", {})
        resp = personality.get("response", {})
        emot = personality.get("emotion", {})
        self_perc = personality.get("self_perception", {})
        
        verbose = comm.get("verbose", 50)
        technical = comm.get("technical", 50)
        confidence = resp.get("confidence", 50)
        nervousness = emot.get("nervousness", 20)
        storytelling = resp.get("storytelling", 50)
        enthusiasm = emot.get("enthusiasm", 70)
        self_awareness = self_perc.get("self_awareness", 50)
        
        # 格式化知识盲区
        knowledge_blind_spots = self._format_knowledge_blind_spots()
        
        # 构建完整提示词
        system_prompt = CANDIDATE_SYSTEM_PROMPT.format(
            skill_profile=skill_profile,
            work_experience=work_experience,
            personality_traits=personality_traits,
            knowledge_blind_spots=knowledge_blind_spots,
            verbose=verbose,
            technical=technical,
            confidence=confidence,
            nervousness=nervousness,
            storytelling=storytelling,
            enthusiasm=enthusiasm,
            self_awareness=self_awareness
        )
        
        return system_prompt
    
    def _format_knowledge_blind_spots(self) -> str:
        """格式化知识盲区描述"""
        if not self.profile.knowledge_blind_spots:
            return "无明显知识盲区（能够准确评估自己的能力）"
        
        blind_spots = self.profile.knowledge_blind_spots
        overconfident = blind_spots.get("overconfident_areas", [])
        underconfident = blind_spots.get("underconfident_areas", [])
        
        result = []
        
        if overconfident:
            result.append("**过度自信领域（容易不懂装懂）:**")
            for area in overconfident:
                skill = area.get("skill", "未知")
                actual = area.get("actual_level", 0)
                perceived = area.get("perceived_level", 0)
                desc = area.get("description", "")
                result.append(f"- {skill}: 实际能力{actual}/10，自我感觉{perceived}/10")
                result.append(f"  {desc}")
        
        if underconfident:
            result.append("\n**过度谦虚领域（容易低估自己）:**")
            for area in underconfident:
                skill = area.get("skill", "未知")
                actual = area.get("actual_level", 0)
                perceived = area.get("perceived_level", 0)
                desc = area.get("description", "")
                result.append(f"- {skill}: 实际能力{actual}/10，自我感觉{perceived}/10")
                result.append(f"  {desc}")
        
        if not result:
            return "无明显知识盲区（能够准确评估自己的能力）"
        
        return "\n".join(result)
    
    def _apply_personality_style(self, base_answer: str) -> str:
        """
        根据性格特质调整回答风格
        （当前版本由LLM直接处理风格，此方法保留用于后期优化）
        
        Args:
            base_answer: 基础回答内容
            
        Returns:
            应用性格风格后的回答
        """
        # Phase 1 中由LLM的系统提示词直接处理风格
        # Phase 2 可以在这里添加后处理逻辑
        return base_answer
