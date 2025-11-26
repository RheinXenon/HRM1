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
        
        # 如果是追问，添加强化约束提示（使用Few-Shot Negative Examples）
        if is_followup:
            user_message += "\n\n**⚠️ 这是追问！面试官在测试你的真实知识深度。**\n\n"
            
            # 获取相关技能的actual_level
            skill_levels = {}
            for skill in related_skills:
                skill_levels[skill] = self.profile.skills.get(skill, 0)
            
            # 使用Few-Shot Negative Examples - 明确展示"错误"和"正确"的回答
            for skill, level in skill_levels.items():
                user_message += f"**你的{skill}技能: actual_level={level}/10**\n\n"
                
                if level <= 3:
                    user_message += "**❌ 错误示例1（绝对不能这样回答）:**\n"
                    user_message += '"我理解依赖数组的原理是React会用Object.is进行浅比较，所以如果传对象会导致引用不同，需要用useCallback来稳定引用..."\n'
                    user_message += "→ 错误！重复了面试官的专业术语：'依赖数组'、'Object.is'、'useCallback'！\n\n"
                    
                    user_message += "**❌ 错误示例2（也不能这样回答）:**\n"
                    user_message += '"cleanup函数的话，我记得是在组件卸载时调用的..."\n'
                    user_message += '"清理函数的话，好像是在组件卸载的时候执行..."\n'
                    user_message += "→ 错误！'cleanup函数'、'清理函数'都是专业术语！应该用'那个...返回的函数'等模糊说法！\n\n"
                    
                    user_message += "**✅ 正确示例（你应该这样回答）:**\n"
                    user_message += '"呃...您问的这几个问题，说实话我都不太清楚具体原理。我们项目里就是照着文档或者别人的代码写的，为什么要那样传参数、什么时候会执行，这些底层的东西我真没研究过。"\n'
                    user_message += "→ 正确！完全避免了专业术语，用'这个'、'那样'等模糊词汇，诚实承认不懂。\n\n"
                    
                    user_message += "**你的词汇限制:**\n"
                    user_message += "- ✅ 可以说: '不太清楚'、'记不住了'、'没研究过'、'听说过但不会用'\n"
                    user_message += "- ❌ 禁止说: 任何API名称、配置参数、技术术语、工作原理\n\n"
                    
                elif level <= 5:
                    user_message += "**❌ 错误示例（绝对不能这样回答）:**\n"
                    user_message += '"RabbitMQ消息不丢失需要配置publisher confirm、durable队列、persistent消息，还要处理mandatory参数和消费端的手动ACK..."\n'
                    user_message += "→ 这是错误的！你actual_level=5，不可能知道这么多具体配置参数！\n\n"
                    
                    user_message += "**✅ 正确示例（你应该这样回答）:**\n"
                    user_message += '"嗯...我们项目里确实配置了一些保证消息可靠性的东西，好像是要配置队列的某些参数？具体叫什么参数我记不清了，当时是跟着同事配的，这块我了解得不够深入。"\n'
                    user_message += "→ 这才符合你的真实水平！知道概念但说不出具体参数名。\n\n"
                    
                    user_message += "**你的词汇限制:**\n"
                    user_message += "- ✅ 可以说: '配置了一些参数'、'设置了某些选项'、'好像是...'\n"
                    user_message += "- ❌ 禁止说: 具体的配置参数名、API名称、高级特性术语\n\n"
            
            user_message += "\n**核心原则: 你的actual_level决定了你的'词汇表'大小**\n"
            user_message += "- 追问不会让你'突然想起'新的专业术语\n"
            user_message += "- 如果你之前没说过某个术语，现在也不能突然说出来\n"
            user_message += "- **即使面试官问题中提到某个术语，如果超出你的能力，也不要重复使用它**\n"
            user_message += "- 用'这个'、'那个'、'某些功能'等模糊词汇代替你不懂的专业术语\n"
            user_message += "- 当答不上来时，直接承认不知道，不要试图'圆'\n\n"
        
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
            answer = self.llm_client.chat_completion(
                messages=messages,
                temperature=0.8
            )
            
            # 记录对话历史
            self.conversation_history.append({
                "role": "interviewer",
                "type": "question",
                "content": question,
                "context": question_context
            })
            self.conversation_history.append({
                "role": "candidate",
                "type": "answer",
                "content": answer
            })
            
            logger.success(f"✅ 回答生成成功 (上下文: {len(messages)}条消息)")
            return answer.strip()
            
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
