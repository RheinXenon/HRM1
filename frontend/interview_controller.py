"""
面试控制器
管理面试流程的启动、暂停、继续、中止等操作
支持实时流式输出面试对话
"""

import sys
import json
import threading
import queue
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import InterviewEngine
from config import load_candidate_template, generate_domain_config
from core.personality_generator import PersonalityGenerator, create_random_candidate_config
from core.random_generator import RandomCandidateGenerator
from dataclasses import asdict


class InterviewController:
    """面试控制器类"""
    
    def __init__(self):
        self.engine = None
        self.interview_thread = None
        self.is_running = False
        self.is_paused = False
        self.message_queue = queue.Queue()
        self.current_interview = None
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self._domain_config_cache = {}  # 缓存领域配置
        
    def start_interview(
        self,
        domain_id: str,
        candidate_configs: List[Dict],
        mode: str = "full",
        callback: Optional[Callable] = None,
        enable_memory: bool = True,
        enable_reflection: bool = True
    ):
        """
        启动面试
        
        Args:
            domain_id: 领域ID
            candidate_configs: 候选人配置列表
            mode: 面试模式 (demo/full)
            callback: 回调函数，用于更新UI
            enable_memory: 是否启用记忆系统
            enable_reflection: 是否启用反思机制
        """
        if self.is_running:
            self.message_queue.put({
                "type": "error",
                "content": "已有面试正在进行中"
            })
            return
        
        self.stop_flag.clear()
        self.pause_flag.clear()
        self.is_running = True
        self.is_paused = False
        
        # 创建面试线程
        self.interview_thread = threading.Thread(
            target=self._run_interview_thread,
            args=(domain_id, candidate_configs, mode, callback, enable_memory, enable_reflection),
            daemon=True
        )
        self.interview_thread.start()
        
    def pause_interview(self):
        """暂停面试"""
        if self.is_running and not self.is_paused:
            self.pause_flag.set()
            self.is_paused = True
            self.message_queue.put({
                "type": "system",
                "content": "⏸️ 面试已暂停"
            })
            
    def resume_interview(self):
        """继续面试"""
        if self.is_running and self.is_paused:
            self.pause_flag.clear()
            self.is_paused = False
            self.message_queue.put({
                "type": "system",
                "content": "▶️ 面试继续"
            })
            
    def stop_interview(self):
        """中止面试"""
        if self.is_running:
            self.stop_flag.set()
            self.pause_flag.clear()  # 如果暂停中，先取消暂停
            self.message_queue.put({
                "type": "system",
                "content": "⏹️ 面试已中止"
            })
            
    def get_message(self) -> Optional[Dict]:
        """获取消息队列中的消息"""
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None
            
    def _run_interview_thread(
        self,
        domain_id: str,
        candidate_configs: List[Dict],
        mode: str,
        callback: Optional[Callable],
        enable_memory: bool = True,
        enable_reflection: bool = True
    ):
        """在独立线程中运行面试"""
        try:
            total_candidates = len(candidate_configs)
            
            # 一次性加载领域配置，所有候选人共用
            if domain_id not in self._domain_config_cache:
                company_config, job_config = generate_domain_config(domain_id)
                self._domain_config_cache[domain_id] = (company_config, job_config)
            else:
                company_config, job_config = self._domain_config_cache[domain_id]
            
            for idx, candidate_config in enumerate(candidate_configs, 1):
                # 检查中止标志
                if self.stop_flag.is_set():
                    break
                
                # 发送批量进度更新
                self.message_queue.put({
                    "type": "batch_progress",
                    "content": {
                        "current": idx,
                        "total": total_candidates
                    }
                })
                
                # 如果是批量模式且不是第一个，清空之前的消息
                if total_candidates > 1 and idx > 1:
                    self.message_queue.put({
                        "type": "clear_messages",
                        "content": {}
                    })
                
                self.message_queue.put({
                    "type": "system",
                    "content": f"🚀 开始第 {idx}/{total_candidates} 个面试 (领域: {domain_id})"
                })
                
                # 创建面试引擎（启用记忆和反思）
                self.engine = InterviewEngine(
                    enable_memory=enable_memory,
                    enable_reflection=enable_reflection
                )
                
                # 发送候选人信息
                profile = candidate_config.get("profile", candidate_config)
                self.message_queue.put({
                    "type": "candidate_info",
                    "content": {
                        "name": profile.get("name", "未知"),
                        "skills": profile.get("skills", {}),
                        "personality": profile.get("personality", {}),
                        "experience": profile.get("experience", {})
                    }
                })
                
                # 运行面试（通过hook捕获对话）
                self._run_interview_with_hooks(
                    candidate_config, mode, domain_id,
                    company_config, job_config
                )
                
                # 如果还有下一个，等待片刻
                if idx < total_candidates and not self.stop_flag.is_set():
                    self.message_queue.put({
                        "type": "system",
                        "content": "⏳ 准备下一个面试..."
                    })
                    time.sleep(2)
            
        except Exception as e:
            self.message_queue.put({
                "type": "error",
                "content": f"❌ 面试执行错误: {str(e)}"
            })
        finally:
            self.is_running = False
            self.message_queue.put({
                "type": "system",
                "content": "✅ 批量面试流程结束"
            })
            if callback:
                callback()
                
    def _run_interview_with_hooks(
        self,
        candidate_config: Dict,
        mode: str,
        domain_id: str,
        company_config: Dict,
        job_config: Dict
    ):
        """运行面试并通过hooks捕获对话内容"""
        from core.llm_client import LLMClient
        from agents.candidate_agent import CandidateAgent, CandidateProfile
        from agents.interviewer_agent import InterviewerAgent
        from core.resume_generator import ResumeGenerator
        import uuid
        
        start_time = datetime.now()
        interview_id = str(uuid.uuid4())[:8]
        
        # 解析候选人配置
        profile_data = candidate_config.get("profile", candidate_config)
        candidate_profile = CandidateProfile(
            name=profile_data.get("name", "未知"),
            skills=profile_data.get("skills", {}),
            experience=profile_data.get("experience", {}),
            personality=profile_data.get("personality", {}),
            knowledge_blind_spots=profile_data.get("knowledge_blind_spots", None)
        )
        
        # 生成简历
        llm_client = LLMClient()
        resume_generator = ResumeGenerator(llm_client=llm_client)
        resume_data = resume_generator.generate_resume(
            candidate_profile=candidate_profile,
            save_to_file=True
        )
        
        # 检查中止标志
        if self.stop_flag.is_set():
            return
        
        # 发送简历信息
        self.message_queue.put({
            "type": "resume",
            "content": resume_data
        })
        
        # 初始化Agents
        interviewer = InterviewerAgent(
            llm_client=llm_client,
            job_config=job_config,
            company_config=company_config,
            domain_id=domain_id,
            resume_data=resume_data
        )
        
        candidate = CandidateAgent(
            llm_client=llm_client,
            profile=candidate_profile
        )
        
        # 发送公司和职位信息
        self.message_queue.put({
            "type": "interview_info",
            "content": {
                "company": company_config.get("name", ""),
                "job_title": job_config.get("title", ""),
                "candidate_name": candidate_profile.name
            }
        })
        
        # 开场白
        greeting = f"你好，欢迎来到{company_config.get('name', '')}面试{job_config.get('title', '')}职位。我看了你的简历，请先简单介绍一下你自己。"
        self._send_message("interviewer", greeting)
        
        # 等待暂停
        self._wait_if_paused()
        if self.stop_flag.is_set():
            return
        
        # 候选人自我介绍
        introduction = candidate.introduce_self()
        self._send_message("candidate", introduction)
        
        conversation_log = [
            {"role": "interviewer", "content": greeting},
            {"role": "candidate", "content": introduction}
        ]
        
        # 生成面试问题
        candidate_level = profile_data.get("experience", {}).get("level", "senior")
        questions = interviewer.generate_interview_script(candidate_level)
        resume_questions = interviewer.generate_resume_based_questions()
        
        if resume_questions:
            questions = resume_questions + questions
        
        if mode == "demo":
            questions = questions[:3]
        
        self.message_queue.put({
            "type": "system",
            "content": f"📋 生成了 {len(questions)} 个面试问题"
        })
        
        # 问答循环
        for i, question in enumerate(questions, 1):
            # 检查中止标志
            if self.stop_flag.is_set():
                break
            
            # 等待暂停
            self._wait_if_paused()
            
            self.message_queue.put({
                "type": "system",
                "content": f"📝 问题 {i}/{len(questions)} [类别: {question.category}]"
            })
            
            # 面试官提问
            question_text = interviewer.ask_question(question)
            self._send_message("interviewer", question_text, {
                "category": question.category,
                "is_question": True
            })
            
            conversation_log.append({
                "role": "interviewer",
                "content": question_text,
                "category": question.category
            })
            
            # 等待暂停
            self._wait_if_paused()
            if self.stop_flag.is_set():
                break
            
            # 候选人回答
            answer = candidate.answer_question(
                question=question_text,
                question_context={
                    "category": question.category,
                    "expected_skills": question.expected_skills
                }
            )
            self._send_message("candidate", answer)
            
            conversation_log.append({
                "role": "candidate",
                "content": answer
            })
            
            # 评估回答
            evaluation = interviewer.evaluate_answer(
                question=question_text,
                answer=answer,
                target_skills=question.expected_skills
            )
            
            normalized_score = evaluation.get("normalized_score", 50.0)
            score_interpretation = evaluation.get("score_interpretation", {})
            recommendation = score_interpretation.get("recommendation", "观察")
            
            # 将评估结果添加到对话日志（供记忆系统使用）
            evaluation_summary = f"标准化评分: {normalized_score:.1f}/100, 建议: {recommendation}"
            if evaluation.get("feedback"):
                evaluation_summary += f", 反馈: {evaluation.get('feedback')}"
            
            conversation_log.append({
                "role": "system",
                "content": evaluation_summary
            })
            
            self.message_queue.put({
                "type": "evaluation",
                "content": {
                    "score": normalized_score,
                    "recommendation": recommendation,
                    "feedback": evaluation.get("feedback", "")
                }
            })
            
            # 追问机制（简化版）
            confidence_level = evaluation.get("confidence_level", "genuine")
            need_followup = evaluation.get("need_follow_up", "no").lower() == "yes"
            
            if need_followup or confidence_level == "overconfident":
                # 等待暂停
                self._wait_if_paused()
                if self.stop_flag.is_set():
                    break
                
                self.message_queue.put({
                    "type": "system",
                    "content": "🔍 触发追问机制"
                })
                
                followup_skill = question.expected_skills[0] if question.expected_skills else "技术细节"
                followup_question = interviewer.generate_followup_question(
                    skill=followup_skill,
                    original_question=question_text,
                    original_answer=answer,
                    evaluation=evaluation
                )
                
                self._send_message("interviewer", followup_question, {
                    "is_followup": True
                })
                
                # 添加追问问题到对话日志（标记为追问）
                conversation_log.append({
                    "role": "interviewer",
                    "content": followup_question,
                    "type": "followup",
                    "category": question.category
                })
                
                # 等待暂停
                self._wait_if_paused()
                if self.stop_flag.is_set():
                    break
                
                # 候选人回答追问
                followup_answer = candidate.answer_question(
                    question=followup_question,
                    question_context={
                        "category": question.category,
                        "expected_skills": question.expected_skills,
                        "is_followup": True
                    }
                )
                self._send_message("candidate", followup_answer)
                
                # 添加追问回答到对话日志
                conversation_log.append({
                    "role": "candidate",
                    "content": followup_answer
                })
                
                # 评估追问回答
                followup_evaluation = interviewer.evaluate_answer(
                    question=followup_question,
                    answer=followup_answer,
                    target_skills=question.expected_skills
                )
                
                followup_score = followup_evaluation.get("normalized_score", 50.0)
                followup_interp = followup_evaluation.get("score_interpretation", {})
                
                # 构建追问评估摘要（包含关键词）
                followup_eval_summary = f"追问评分: {followup_score:.1f}/100"
                if followup_score < normalized_score - 10:
                    followup_eval_summary += ", 🚩 追问后露怯"
                elif followup_score >= normalized_score:
                    followup_eval_summary += ", 追问后依然扎实"
                
                if followup_evaluation.get("feedback"):
                    followup_eval_summary += f", {followup_evaluation.get('feedback')}"
                
                # 添加追问评估到对话日志
                conversation_log.append({
                    "role": "system",
                    "content": followup_eval_summary
                })
                
                self.message_queue.put({
                    "type": "evaluation",
                    "content": {
                        "score": followup_score,
                        "recommendation": followup_interp.get("recommendation", "观察"),
                        "feedback": followup_evaluation.get("feedback", ""),
                        "is_followup": True
                    }
                })
        
        # 检查是否被中止
        if self.stop_flag.is_set():
            self.message_queue.put({
                "type": "system",
                "content": "⚠️ 面试被用户中止，正在保存当前进度..."
            })
        
        # 候选人提问环节
        interviewer_prompt = "非常好，你还有什么问题要问我吗？"
        self._send_message("interviewer", interviewer_prompt)
        conversation_log.append({
            "role": "interviewer",
            "content": interviewer_prompt
        })
        
        self._wait_if_paused()
        
        candidate_questions = candidate.ask_question_to_interviewer()
        self._send_message("candidate", candidate_questions)
        conversation_log.append({
            "role": "candidate",
            "content": candidate_questions
        })
        
        # 生成最终报告
        self.message_queue.put({
            "type": "system",
            "content": "📊 正在生成评估报告..."
        })
        
        final_report = interviewer.generate_final_report(candidate_profile.name)
        
        end_time = datetime.now()
        
        # 保存面试记录
        from core.interview_engine import InterviewResult
        
        result = InterviewResult(
            interview_id=interview_id,
            candidate_name=candidate_profile.name,
            job_title=job_config.get("title", ""),
            start_time=start_time,
            end_time=end_time,
            conversation_log=conversation_log,
            evaluation=final_report,
            recommendation_score=final_report.get("recommendation_score", 0),
            summary=final_report.get("summary", "")
        )
        
        self.engine._save_interview_record(result, resume_data=resume_data)
        self.current_interview = result
        
        # Phase 2: 保存记忆和反思（每个候选人面试结束后）
        duration = (end_time - start_time).total_seconds()
        interview_data = {
            "interview_id": interview_id,
            "candidate_name": candidate_profile.name,
            "job_title": job_config.get("title", ""),
            "conversation_log": conversation_log,
            "evaluation": final_report,
            "recommendation_score": final_report.get("recommendation_score", 0),
            "duration_seconds": duration
        }
        
        # 提取情节记忆
        if self.engine.memory_system:
            self.message_queue.put({
                "type": "system",
                "content": "📚 正在保存面试记忆..."
            })
            episodes = self.engine.memory_system.extract_episodes_from_interview(interview_data)
            for episode in episodes:
                self.engine.memory_system.add_episodic_memory(episode)
            
            # 更新语义记忆
            self.engine.memory_system.update_semantic_from_episodes()
            
            # 保存记忆
            self.engine.memory_system.save_memories()
            
            # 清空短期记忆
            self.engine.memory_system.clear_working_memory()
            
            self.message_queue.put({
                "type": "system",
                "content": f"✅ 已保存 {len(episodes)} 个情节记忆"
            })
        
        # 触发即时反思
        if self.engine.reflection_system:
            self.message_queue.put({
                "type": "system",
                "content": "🤔 正在进行面试反思..."
            })
            reflection = self.engine.reflection_system.immediate_reflection(interview_data)
            
            # 保存反思数据
            self.engine.reflection_system.save_all()
            
            self.message_queue.put({
                "type": "system",
                "content": f"✅ 反思完成: {len(reflection.findings)} 项发现, {len(reflection.improvement_suggestions)} 条建议"
            })
        
        # 发送最终报告
        self.message_queue.put({
            "type": "final_report",
            "content": final_report
        })
        
    def _send_message(self, role: str, content: str, metadata: Dict = None):
        """发送消息到队列"""
        message = {
            "type": "message",
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            message["metadata"] = metadata
        self.message_queue.put(message)
        
        # 模拟流式输出的延迟
        time.sleep(0.1)
        
    def _wait_if_paused(self):
        """如果暂停，则等待继续信号"""
        while self.pause_flag.is_set() and not self.stop_flag.is_set():
            time.sleep(0.1)
