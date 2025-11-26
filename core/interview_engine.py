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
from core.resume_generator import ResumeGenerator
from core.candidate_analyzer import CandidateAnalyzer


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
        self.analyzer = CandidateAnalyzer(noise_level=0.05)  # 初始化候选人分析器（模拟器）
        
    def _create_llm_client(self):
        """创建LLM客户端"""
        return LLMClient()
    
    def run_interview(
        self,
        candidate_config: Dict,
        mode: str = "demo",
        domain_id: str = "tech",
        job_config: Optional[Dict] = None,
        company_config: Optional[Dict] = None,
        job_file: Optional[str] = None,
        company_file: Optional[str] = None
    ) -> InterviewResult:
        """
        执行一次完整的面试流程
        
        Args:
            candidate_config: 候选人配置字典
            mode: 面试模式 ("demo" 或 "full")
            domain_id: 领域ID（tech/marketing/healthcare等），默认为tech
            job_config: 职位配置字典（优先）
            company_config: 公司配置字典（优先）
            job_file: 职位配置文件名（向后兼容）
            company_file: 公司配置文件名（向后兼容）
            
        Returns:
            面试结果对象
        """
        logger.info("="*60)
        logger.info("🚀 开始面试流程")
        logger.info("="*60)
        
        start_time = datetime.now()
        interview_id = str(uuid.uuid4())[:8]
        
        # 1. 加载/生成配置
        logger.info("📋 步骤1: 加载配置...")
        
        # 优先使用传入的配置字典，否则从文件加载，最后使用动态生成
        if job_config is None:
            if job_file:
                job_config = load_job_config(job_file)
            else:
                # 动态生成
                from config import generate_domain_config
                company_config, job_config = generate_domain_config(domain_id)
        
        if company_config is None:
            if company_file:
                company_config = load_company_config(company_file)
            else:
                # 如果job_config是动态生成的，company_config已经生成了
                if not job_file:
                    from config import generate_domain_config
                    company_config, _ = generate_domain_config(domain_id)
        
        # 2. 解析候选人配置
        logger.info("🤖 步骤2: 解析候选人配置...")
        
        profile_data = candidate_config.get("profile", candidate_config)
        candidate_profile = CandidateProfile(
            name=profile_data.get("name", "未知"),
            skills=profile_data.get("skills", {}),
            experience=profile_data.get("experience", {}),
            personality=profile_data.get("personality", {}),
            knowledge_blind_spots=profile_data.get("knowledge_blind_spots", None)
        )
        
        # 3. 生成候选人简历
        logger.info("📄 步骤3: 生成候选人简历...")
        resume_generator = ResumeGenerator(llm_client=self.llm_client)
        resume_data = resume_generator.generate_resume(
            candidate_profile=candidate_profile,
            save_to_file=True
        )
        
        # 显示简历
        resume_display = ResumeGenerator.format_resume_for_display(resume_data)
        print("\n" + resume_display)
        
        # 4. 初始化Agents
        logger.info("🤖 步骤4: 初始化面试官和候选人Agent...")
        
        # 创建面试官Agent（传入简历数据）
        interviewer = InterviewerAgent(
            llm_client=self.llm_client,
            job_config=job_config,
            company_config=company_config,
            domain_id=domain_id,
            resume_data=resume_data
        )
        
        # 创建候选人Agent
        candidate = CandidateAgent(
            llm_client=self.llm_client,
            profile=candidate_profile
        )
        
        logger.success(f"✅ 面试官和候选人 {candidate_profile.name} 就位")
        
        # 5. 开场白
        logger.info("\n👋 步骤5: 面试开场...")
        print("\n" + "="*60)
        print(f"🏛️  {company_config.get('name', '')}") 
        print(f"💼 {job_config.get('title', '')} 职位面试")
        print(f"👤 候选人: {candidate_profile.name}")
        print("="*60)
        
        greeting = f"你好，欢迎来到{company_config.get('name', '')}面试{job_config.get('title', '')}职位。我看了你的简历，请先简单介绍一下你自己。"
        print(f"\n👔 面试官: {greeting}")
        
        # 6. 自我介绍
        introduction = candidate.introduce_self()
        print(f"\n👤 {candidate_profile.name}: {introduction}")
        
        conversation_log = [
            {"role": "interviewer", "content": greeting},
            {"role": "candidate", "content": introduction}
        ]
        
        # 7. 生成面试问题（包含基于简历的问题）
        logger.info("\n❓ 步骤6: 生成面试问题...")
        candidate_level = profile_data.get("experience", {}).get("level", "senior")
        
        # 生成常规问题
        questions = interviewer.generate_interview_script(candidate_level)
        
        # 生成基于简历的针对性问题
        resume_questions = interviewer.generate_resume_based_questions()
        
        # 将基于简历的问题插入到问题列表前面（前2-3个）
        if resume_questions:
            questions = resume_questions + questions
        
        # 根据模式选择问题数量
        if mode == "demo":
            questions = questions[:3]  # demo模式只问3个问题
            logger.info(f"🎯 Demo模式: 将进行 {len(questions)} 个问题")
        else:
            logger.info(f"🎯 Full模式: 将进行 {len(questions)} 个问题")
        
        # 8. 问答循环
        logger.info("\n💬 步骤7: 开始问答环节...\n")
        
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
            
            # === 候选人回答分析（模拟AI模型） ===
            # 将 CandidateProfile 转为字典
            profile_dict = {
                "name": candidate_profile.name,
                "skills": candidate_profile.skills,
                "experience": candidate_profile.experience,
                "personality": candidate_profile.personality,
                "knowledge_blind_spots": candidate_profile.knowledge_blind_spots
            }
            
            analysis_result = self.analyzer.analyze_answer(
                answer=answer,
                question=question_text,
                target_skills=question.expected_skills,
                candidate_profile=profile_dict
            )
            
            # 格式化并显示分析结果
            analysis_display = CandidateAnalyzer.format_analysis_result(analysis_result)
            print(f"\n{analysis_display}")
            
            # 将分析结果添加到对话日志
            conversation_log.append({
                "role": "system",
                "type": "candidate_analysis",
                "content": analysis_result,
                "display": analysis_display
            })
            
            # 评估回答
            evaluation = interviewer.evaluate_answer(
                question=question_text,
                answer=answer,
                target_skills=question.expected_skills
            )
            
            # Phase 1: 使用新的标准化评分 (0-100)
            normalized_score = evaluation.get("normalized_score", 50.0)
            score_interpretation = evaluation.get("score_interpretation", {})
            recommendation = score_interpretation.get("recommendation", "观察")
            
            # 兼容旧代码：保留1-10分制的score字段
            old_score = evaluation.get("score", int(normalized_score / 10))
            
            print(f"\n📊 [评分: {normalized_score:.1f}/100 - {recommendation}]")
            
            conversation_log.append({
                "role": "system",
                "content": f"标准化评分: {normalized_score:.1f}/100, 建议: {recommendation}"
            })
            
            # ===== 追问机制 =====
            # 优先使用LLM评估结果判断是否需要追问
            confidence_level = evaluation.get("confidence_level", "genuine")
            need_followup_by_llm = evaluation.get("need_follow_up", "no").lower() == "yes"
            
            # 同时使用规则检测作为辅助 (传入旧分数用于兼容)
            detection = interviewer.detect_shallow_answer(
                answer=answer,
                target_skills=question.expected_skills,
                score=old_score
            )
            
            # 综合判断：LLM判定过度自信 或 规则检测可疑且得分较高
            # Phase 1: 使用标准化分数判断 (0-100分制)
            # 降低阈值以提高追问触发率：
            # - 可疑度>=3 且 分数>=50（中等水平）
            # - 可疑度>=2 且 分数>=65（良好水平） 
            should_followup = (
                (confidence_level == "overconfident" and need_followup_by_llm) or
                (detection["is_suspicious"] and normalized_score >= 45) or  # 降低基础阈值
                (detection.get("suspicion_score", 0) >= 3 and normalized_score >= 50) or  # 降低中等阈值
                (detection.get("suspicion_score", 0) >= 2 and normalized_score >= 65)  # 新增：轻度可疑+高分也追问
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
                
                # === 追问后的分析 ===
                followup_analysis_result = self.analyzer.analyze_answer(
                    answer=followup_answer,
                    question=followup_question,
                    target_skills=question.expected_skills,
                    candidate_profile=profile_dict  # 使用同一个档案字典
                )
                
                # 显示追问后的分析结果
                followup_analysis_display = CandidateAnalyzer.format_analysis_result(followup_analysis_result)
                print(f"\n{followup_analysis_display}")
                
                # 添加到对话日志
                conversation_log.append({
                    "role": "system",
                    "type": "candidate_analysis",
                    "content": followup_analysis_result,
                    "display": followup_analysis_display,
                    "is_followup": True
                })
                
                # 重新评估追问后的回答
                followup_evaluation = interviewer.evaluate_answer(
                    question=followup_question,
                    answer=followup_answer,
                    target_skills=question.expected_skills
                )
                
                # Phase 1: 使用标准化评分比较
                followup_normalized_score = followup_evaluation.get("normalized_score", 50.0)
                followup_interpretation = followup_evaluation.get("score_interpretation", {})
                followup_recommendation = followup_interpretation.get("recommendation", "观察")
                
                # 比较前后评分 (0-100分制)
                score_drop = normalized_score - followup_normalized_score
                
                if score_drop >= 20:
                    # 追问后分数下降明显(≥20分)，说明确实不懂装懂
                    final_normalized_score = followup_normalized_score
                    flag = "🚩 追问后露怯"
                    print(f"\n📊 [追问评分: {followup_normalized_score:.1f}/100 - {followup_recommendation}] {flag}")
                    print(f"⚠️  评分从 {normalized_score:.1f} 降至 {followup_normalized_score:.1f}，怀疑不懂装懂")
                elif followup_normalized_score >= normalized_score:
                    # 追问后回答依然好，可能确实懂
                    final_normalized_score = followup_normalized_score
                    flag = "✅ 追问后依然扎实"
                    print(f"\n📊 [追问评分: {followup_normalized_score:.1f}/100 - {followup_recommendation}] {flag}")
                else:
                    # 轻微下降(<20分)，取平均
                    final_normalized_score = (normalized_score + followup_normalized_score) / 2
                    flag = "⚡ 追问后略有下降"
                    print(f"\n📊 [追问评分: {followup_normalized_score:.1f}/100 - {followup_recommendation}] {flag}")
                
                conversation_log.append({
                    "role": "system",
                    "content": f"追问评分: {followup_normalized_score:.1f}/100, 最终: {final_normalized_score:.1f}/100, 标记: {flag}"
                })
                
                # 更新评估分数 (同时更新新旧两种格式)
                evaluation["normalized_score"] = final_normalized_score
                evaluation["original_normalized_score"] = normalized_score
                evaluation["followup_normalized_score"] = followup_normalized_score
                evaluation["score"] = int(final_normalized_score / 10)  # 兼容旧格式
                evaluation["original_score"] = old_score
                evaluation["followup_score"] = int(followup_normalized_score / 10)
                evaluation["followup_flag"] = flag
        
        # 9. 候选人提问
        logger.info("\n❔ 步骤8: 候选人提问环节...")
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
        
        # 10. 生成最终报告
        logger.info("\n📊 步骤9: 生成评估报告...")
        final_report = interviewer.generate_final_report(candidate_profile.name)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 11. 构建结果
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
        
        # 12. 保存记录（包含简历数据）
        self._save_interview_record(result, resume_data=resume_data)
        
        # 输出结果
        print("\n" + "="*60)
        print("🎆 面试结束")
        print("="*60)
        logger.success(f"✅ 面试完成! 耗时: {duration:.1f}秒")
        logger.info(f"📝 推荐度: {result.recommendation_score}/100")
        logger.info(f"📁 面试ID: {interview_id}")
        
        return result
    
    
    def _save_interview_record(self, result: InterviewResult, resume_data: Dict = None):
        """
        保存面试记录到数据库
        
        Args:
            result: 面试结果
            resume_data: 候选人简历数据（可选）
        """
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
            "resume": resume_data,  # 新增：保存简历数据
            "conversation_log": result.conversation_log,
            "evaluation": result.evaluation,
            "recommendation_score": result.recommendation_score,
            "summary": result.summary
        }
        
        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.success(f"💾 面试记录已保存: {filepath}")
