"""
面试引擎
协调面试官Agent和候选人Agent的交互流程
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
import uuid

from core.llm_client import LLMClient
from agents.candidate_agent import CandidateAgent, CandidateProfile
from agents.interviewer_agent import InterviewerAgent, InterviewQuestion
from config import load_job_config, load_company_config


@dataclass
class InterviewResult:
    """面试结果数据类"""
    interview_id: str
    candidate_name: str
    job_title: str
    start_time: datetime
    end_time: datetime
    conversation_log: List[Dict]
    evaluation: Dict[str, Any]
    recommendation_score: int
    summary: str


class InterviewEngine:
    """面试引擎类"""
    
    def __init__(self, llm_client=None):
        """
        初始化面试引擎
        
        Args:
            llm_client: LLM客户端实例，如果为None则自动创建
        """
        self.llm_client = llm_client or self._create_llm_client()
        
    def _create_llm_client(self):
        """创建LLM客户端"""
        return LLMClient()
    
    def run_interview(
        self,
        job_file: str,
        company_file: str,
        candidate_config: Dict,
        mode: str = "demo"
    ) -> InterviewResult:
        """
        执行一次完整的面试流程
        
        Args:
            job_file: 职位配置文件名（不含路径）
            company_file: 公司信息文件名（不含路径）
            candidate_config: 候选人配置字典
            mode: 面试模式 ("demo" 或 "full")
            
        Returns:
            面试结果对象
        """
        logger.info("="*60)
        logger.info("🚀 开始面试流程")
        logger.info("="*60)
        
        start_time = datetime.now()
        interview_id = str(uuid.uuid4())[:8]
        
        # 1. 加载配置
        logger.info("📋 步骤1: 加载配置文件...")
        job_config = load_job_config(job_file)
        company_config = load_company_config(company_file)
        
        # 2. 初始化Agents
        logger.info("🤖 步骤2: 初始化面试官和候选人Agent...")
        
        # 创建面试官Agent
        interviewer = InterviewerAgent(
            llm_client=self.llm_client,
            job_config=job_config,
            company_config=company_config
        )
        
        # 解析候选人配置
        profile_data = candidate_config.get("profile", candidate_config)
        candidate_profile = CandidateProfile(
            name=profile_data.get("name", "未知"),
            skills=profile_data.get("skills", {}),
            experience=profile_data.get("experience", {}),
            personality=profile_data.get("personality", {}),
            knowledge_blind_spots=profile_data.get("knowledge_blind_spots", None)
        )
        
        # 创建候选人Agent
        candidate = CandidateAgent(
            llm_client=self.llm_client,
            profile=candidate_profile
        )
        
        logger.success(f"✅ 面试官和候选人 {candidate_profile.name} 就位")
        
        # 3. 开场白
        logger.info("\n👋 步骤3: 面试开场...")
        print("\n" + "="*60)
        print(f"🏛️  {company_config.get('name', '')}") 
        print(f"💼 {job_config.get('title', '')} 职位面试")
        print(f"👤 候选人: {candidate_profile.name}")
        print("="*60)
        
        greeting = f"你好，欢迎来到{company_config.get('name', '')}面试{job_config.get('title', '')}职位。请先简单介绍一下你自己。"
        print(f"\n👔 面试官: {greeting}")
        
        # 4. 自我介绍
        introduction = candidate.introduce_self()
        print(f"\n👤 {candidate_profile.name}: {introduction}")
        
        conversation_log = [
            {"role": "interviewer", "content": greeting},
            {"role": "candidate", "content": introduction}
        ]
        
        # 5. 生成面试问题
        logger.info("\n❓ 步骤4: 生成面试问题...")
        candidate_level = profile_data.get("experience", {}).get("level", "senior")
        questions = interviewer.generate_interview_script(candidate_level)
        
        # 根据模式选择问题数量
        if mode == "demo":
            questions = questions[:3]  # demo模式只问3个问题
            logger.info(f"🎯 Demo模式: 将进行 {len(questions)} 个问题")
        else:
            logger.info(f"🎯 Full模式: 将进行 {len(questions)} 个问题")
        
        # 6. 问答循环
        logger.info("\n💬 步骤5: 开始问答环节...\n")
        
        for i, question in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"问题 {i}/{len(questions)} [类别: {question.category}]")
            print(f"{'='*60}")
            
            # 面试官提问
            question_text = interviewer.ask_question(question)
            print(f"\n👔 面试官: {question_text}")
            
            conversation_log.append({
                "role": "interviewer",
                "content": question_text,
                "category": question.category
            })
            
            # 候选人回答
            answer = candidate.answer_question(
                question=question_text,
                question_context={
                    "category": question.category,
                    "expected_skills": question.expected_skills
                }
            )
            print(f"\n👤 {candidate_profile.name}: {answer}")
            
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
            
            score = evaluation.get("score", 0)
            print(f"\n📊 [内部评分: {score}/10]")
            
            conversation_log.append({
                "role": "system",
                "content": f"评分: {score}/10"
            })
            
            # ===== 追问机制 =====
            # 优先使用LLM评估结果判断是否需要追问
            confidence_level = evaluation.get("confidence_level", "genuine")
            need_followup_by_llm = evaluation.get("need_follow_up", "no").lower() == "yes"
            
            # 同时使用规则检测作为辅助
            detection = interviewer.detect_shallow_answer(
                answer=answer,
                target_skills=question.expected_skills,
                score=score
            )
            
            # 综合判断：LLM判定过度自信 或 规则检测可疑且得分较高
            # 降低门槛：只要可疑度>= 3分或LLM认为需追问，就追问
            should_followup = (
                (confidence_level == "overconfident" and need_followup_by_llm) or
                (detection["is_suspicious"] and score >= 5) or
                (detection.get("suspicion_score", 0) >= 3 and score >= 6)
            )
            
            if should_followup:
                # 确定追问的技能点
                followup_skill = detection["followup_skill"] or question.expected_skills[0] if question.expected_skills else "技术细节"
                
                # 使用改进的LLM追问生成
                followup_question = interviewer.generate_followup_question(
                    skill=followup_skill,
                    original_question=question_text,
                    original_answer=answer,
                    evaluation=evaluation
                )
                
                print(f"\n🔍 [追问环节]")
                print(f"👔 面试官: {followup_question}")
                
                conversation_log.append({
                    "role": "interviewer",
                    "content": followup_question,
                    "type": "followup",
                    "reason": f"检测到可疑信号: {', '.join(detection['signals'])}"
                })
                
                # 候选人回答追问
                followup_answer = candidate.answer_question(
                    question=followup_question,
                    question_context={
                        "category": question.category,
                        "expected_skills": question.expected_skills,
                        "is_followup": True
                    }
                )
                print(f"\n👤 {candidate_profile.name}: {followup_answer}")
                
                conversation_log.append({
                    "role": "candidate",
                    "content": followup_answer,
                    "type": "followup_answer"
                })
                
                # 重新评估追问后的回答
                followup_evaluation = interviewer.evaluate_answer(
                    question=followup_question,
                    answer=followup_answer,
                    target_skills=question.expected_skills
                )
                
                followup_score = followup_evaluation.get("score", 0)
                
                # 比较前后评分
                score_drop = score - followup_score
                if score_drop >= 2:
                    # 追问后分数下降明显，说明确实不懂装懂
                    final_score = followup_score
                    flag = "🚩 追问后露怯"
                    print(f"\n📊 [追问评分: {followup_score}/10] {flag}")
                    print(f"⚠️  评分从 {score} 降至 {followup_score}，怀疑不懂装懂")
                elif followup_score >= score:
                    # 追问后回答依然好，可能确实懂
                    final_score = followup_score
                    flag = "✅ 追问后依然扎实"
                    print(f"\n📊 [追问评分: {followup_score}/10] {flag}")
                else:
                    # 轻微下降，取平均
                    final_score = (score + followup_score) / 2
                    flag = "⚡ 追问后略有下降"
                    print(f"\n📊 [追问评分: {followup_score}/10] {flag}")
                
                conversation_log.append({
                    "role": "system",
                    "content": f"追问评分: {followup_score}/10, 最终: {final_score}/10, 标记: {flag}"
                })
                
                # 更新评估分数
                evaluation["score"] = final_score
                evaluation["original_score"] = score
                evaluation["followup_score"] = followup_score
                evaluation["followup_flag"] = flag
        
        # 7. 候选人提问
        logger.info("\n❔ 步骤6: 候选人提问环节...")
        print(f"\n{'='*60}")
        print("🤝 候选人提问环节")
        print(f"{'='*60}")
        
        interviewer_prompt = "非常好，你还有什么问题要问我吗？"
        print(f"\n👔 面试官: {interviewer_prompt}")
        
        candidate_questions = candidate.ask_question_to_interviewer()
        print(f"\n👤 {candidate_profile.name}: {candidate_questions}")
        
        conversation_log.append({
            "role": "interviewer",
            "content": interviewer_prompt
        })
        conversation_log.append({
            "role": "candidate",
            "content": candidate_questions
        })
        
        # 8. 生成最终报告
        logger.info("\n📊 步骤7: 生成评估报告...")
        final_report = interviewer.generate_final_report(candidate_profile.name)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 9. 构建结果
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
        
        # 10. 保存记录
        self._save_interview_record(result)
        
        # 输出结果
        print("\n" + "="*60)
        print("🎆 面试结束")
        print("="*60)
        logger.success(f"✅ 面试完成! 耗时: {duration:.1f}秒")
        logger.info(f"📝 推荐度: {result.recommendation_score}/100")
        logger.info(f"📁 面试ID: {interview_id}")
        
        return result
    
    
    def _save_interview_record(self, result: InterviewResult):
        """保存面试记录到数据库"""
        # Phase 1: 保存为JSON文件
        data_dir = Path("data/interviews")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = result.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{result.interview_id}.json"
        filepath = data_dir / filename
        
        # 将结果转为JSON
        data = {
            "interview_id": result.interview_id,
            "candidate_name": result.candidate_name,
            "job_title": result.job_title,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat(),
            "duration_seconds": (result.end_time - result.start_time).total_seconds(),
            "conversation_log": result.conversation_log,
            "evaluation": result.evaluation,
            "recommendation_score": result.recommendation_score,
            "summary": result.summary
        }
        
        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.success(f"💾 面试记录已保存: {filepath}")
