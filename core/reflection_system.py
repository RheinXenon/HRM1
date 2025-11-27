"""
Agent反思与自我改进机制
实现三级反思：即时反思、阶段性反思、深度反思
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from pathlib import Path
from loguru import logger
from collections import defaultdict
import statistics


@dataclass
class ReflectionResult:
    """反思结果数据类"""
    reflection_id: str
    reflection_level: str  # "immediate" / "periodic" / "deep"
    timestamp: datetime
    
    # 反思内容
    focus_areas: List[str]  # 关注的领域
    findings: List[Dict]  # 发现的问题和亮点
    insights: List[str]  # 洞察和总结
    
    # 改进建议
    improvement_suggestions: List[Dict]  # 改进建议列表
    priority_actions: List[str]  # 优先行动项
    
    # 元数据
    related_interviews: List[str] = field(default_factory=list)
    confidence: float = 0.5
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReflectionResult':
        """从字典创建"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class ReflectionSystem:
    """反思系统管理器"""
    
    def __init__(self, llm_client, storage_dir: str = "data/reflections"):
        """
        初始化反思系统
        
        Args:
            llm_client: LLM客户端
            storage_dir: 存储目录
        """
        self.llm_client = llm_client
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 反思历史
        self.reflection_history: List[ReflectionResult] = []
        
        # 改进追踪
        self.improvements_applied: List[Dict] = []
        
        # 统计信息
        self.stats = {
            "total_reflections": 0,
            "immediate_reflections": 0,
            "periodic_reflections": 0,
            "deep_reflections": 0,
            "improvements_suggested": 0,
            "improvements_applied": 0
        }
        
        # 加载历史反思
        self._load_reflections()
        
        logger.info(f"🤔 反思系统初始化完成: {len(self.reflection_history)} 条历史反思")
    
    # ==================== Level 1: 即时反思 ====================
    
    def immediate_reflection(self, interview_data: Dict) -> ReflectionResult:
        """
        即时反思：每次面试结束后
        
        Args:
            interview_data: 单次面试的完整数据
            
        Returns:
            反思结果
        """
        logger.info("🔍 开始即时反思（面试后）...")
        
        interview_id = interview_data.get("interview_id", "unknown")
        conversation_log = interview_data.get("conversation_log", [])
        evaluation = interview_data.get("evaluation", {})
        
        # 分析维度
        findings = []
        
        # 1. 提问质量分析
        question_quality = self._analyze_question_quality(conversation_log)
        if question_quality:
            findings.append({
                "dimension": "提问质量",
                "score": question_quality.get("score", 0),
                "details": question_quality.get("details", ""),
                "type": "positive" if question_quality.get("score", 0) >= 7 else "concern"
            })
        
        # 2. 追问效果评估
        followup_effectiveness = self._analyze_followup_effectiveness(conversation_log)
        if followup_effectiveness:
            findings.append({
                "dimension": "追问效果",
                "score": followup_effectiveness.get("score", 0),
                "details": followup_effectiveness.get("details", ""),
                "cases": followup_effectiveness.get("cases", []),  # 传递具体案例
                "type": "positive" if followup_effectiveness.get("score", 0) >= 7 else "concern"
            })
        
        # 3. 评分一致性检查
        scoring_consistency = self._analyze_scoring_consistency(conversation_log)
        if scoring_consistency:
            findings.append({
                "dimension": "评分一致性",
                "score": scoring_consistency.get("score", 0),
                "details": scoring_consistency.get("details", ""),
                "type": "positive" if scoring_consistency.get("score", 0) >= 7 else "concern"
            })
        
        # 4. 时间分配分析
        time_allocation = self._analyze_time_allocation(interview_data)
        if time_allocation:
            findings.append({
                "dimension": "时间分配",
                "score": time_allocation.get("score", 0),
                "details": time_allocation.get("details", ""),
                "type": "neutral"
            })
        
        # 生成洞察
        insights = self._generate_insights_from_findings(findings)
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(findings)
        
        # 提取优先行动项
        priority_actions = [
            sugg["action"] for sugg in improvement_suggestions 
            if sugg.get("priority") == "high"
        ][:3]
        
        # 创建反思结果
        reflection_id = f"imm_{interview_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = ReflectionResult(
            reflection_id=reflection_id,
            reflection_level="immediate",
            timestamp=datetime.now(),
            focus_areas=["提问质量", "追问效果", "评分一致性", "时间分配"],
            findings=findings,
            insights=insights,
            improvement_suggestions=improvement_suggestions,
            priority_actions=priority_actions,
            related_interviews=[interview_id],
            confidence=0.7
        )
        
        # 保存反思
        self.reflection_history.append(result)
        self.stats["total_reflections"] += 1
        self.stats["immediate_reflections"] += 1
        self.stats["improvements_suggested"] += len(improvement_suggestions)
        
        self._save_reflection(result)
        
        logger.success(f"✅ 即时反思完成: {len(findings)} 项发现, {len(improvement_suggestions)} 条建议")
        return result
    
    # ==================== Level 2: 阶段性反思 ====================
    
    def periodic_reflection(self, interview_batch: List[Dict], batch_size: int = 10) -> ReflectionResult:
        """
        阶段性反思：每10-20次面试后
        
        Args:
            interview_batch: 最近的面试数据列表
            batch_size: 批次大小
            
        Returns:
            反思结果
        """
        logger.info(f"📊 开始阶段性反思（{len(interview_batch)} 次面试）...")
        
        findings = []
        
        # 1. 识别重复出现的问题
        recurring_issues = self._identify_recurring_issues(interview_batch)
        if recurring_issues:
            findings.append({
                "dimension": "重复问题",
                "count": len(recurring_issues),
                "details": f"发现 {len(recurring_issues)} 类重复出现的问题",
                "issues": recurring_issues,
                "type": "concern"
            })
        
        # 2. 评估追问策略有效性
        followup_stats = self._evaluate_followup_strategy(interview_batch)
        if followup_stats:
            findings.append({
                "dimension": "追问策略统计",
                "true_positive_rate": followup_stats.get("true_positive_rate", 0),
                "false_positive_rate": followup_stats.get("false_positive_rate", 0),
                "details": followup_stats.get("summary", ""),
                "type": "positive" if followup_stats.get("true_positive_rate", 0) >= 0.7 else "concern"
            })
        
        # 3. 分析评分偏差趋势
        scoring_bias = self._analyze_scoring_bias_trend(interview_batch)
        if scoring_bias:
            findings.append({
                "dimension": "评分偏差趋势",
                "bias_direction": scoring_bias.get("direction", "neutral"),
                "magnitude": scoring_bias.get("magnitude", 0),
                "details": scoring_bias.get("details", ""),
                "type": "concern" if abs(scoring_bias.get("magnitude", 0)) > 10 else "neutral"
            })
        
        # 4. 总结成功经验和失败教训
        lessons = self._extract_lessons_learned(interview_batch)
        
        # 生成洞察
        insights = self._generate_periodic_insights(findings, lessons)
        
        # 生成策略调整方案
        improvement_suggestions = self._generate_strategy_adjustments(findings, lessons)
        
        # 优先行动项
        priority_actions = [
            sugg["action"] for sugg in improvement_suggestions 
            if sugg.get("priority") == "high"
        ][:5]
        
        # 创建反思结果
        reflection_id = f"per_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = ReflectionResult(
            reflection_id=reflection_id,
            reflection_level="periodic",
            timestamp=datetime.now(),
            focus_areas=["重复问题", "追问策略", "评分偏差", "经验总结"],
            findings=findings,
            insights=insights,
            improvement_suggestions=improvement_suggestions,
            priority_actions=priority_actions,
            related_interviews=[iv.get("interview_id", "") for iv in interview_batch],
            confidence=0.8
        )
        
        # 保存反思
        self.reflection_history.append(result)
        self.stats["total_reflections"] += 1
        self.stats["periodic_reflections"] += 1
        self.stats["improvements_suggested"] += len(improvement_suggestions)
        
        self._save_reflection(result)
        
        logger.success(f"✅ 阶段性反思完成: {len(findings)} 项发现, {len(improvement_suggestions)} 条建议")
        return result
    
    # ==================== Level 3: 深度反思 ====================
    
    def deep_reflection(self, all_interviews: List[Dict]) -> ReflectionResult:
        """
        深度反思：系统性分析
        
        Args:
            all_interviews: 所有面试数据
            
        Returns:
            反思结果
        """
        logger.info(f"🧐 开始深度反思（{len(all_interviews)} 次面试）...")
        
        findings = []
        
        # 1. 重新审视评估框架的合理性
        framework_review = self._review_assessment_framework(all_interviews)
        if framework_review:
            findings.append({
                "dimension": "评估框架审查",
                "validity": framework_review.get("validity", 0),
                "details": framework_review.get("details", ""),
                "type": "insight"
            })
        
        # 2. 检讨核心假设
        assumption_review = self._review_core_assumptions(all_interviews)
        if assumption_review:
            findings.append({
                "dimension": "核心假设检讨",
                "assumptions": assumption_review.get("assumptions", []),
                "details": assumption_review.get("details", ""),
                "type": "insight"
            })
        
        # 3. 识别系统性偏见
        bias_analysis = self._identify_systematic_bias(all_interviews)
        if bias_analysis:
            findings.append({
                "dimension": "系统性偏见",
                "biases": bias_analysis.get("biases", []),
                "details": bias_analysis.get("details", ""),
                "type": "concern"
            })
        
        # 生成深度洞察
        insights = self._generate_deep_insights(findings)
        
        # 生成系统级优化建议
        improvement_suggestions = self._generate_system_improvements(findings)
        
        # 优先行动项
        priority_actions = [
            sugg["action"] for sugg in improvement_suggestions 
            if sugg.get("priority") == "critical"
        ]
        
        # 创建反思结果
        reflection_id = f"deep_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = ReflectionResult(
            reflection_id=reflection_id,
            reflection_level="deep",
            timestamp=datetime.now(),
            focus_areas=["评估框架", "核心假设", "系统偏见"],
            findings=findings,
            insights=insights,
            improvement_suggestions=improvement_suggestions,
            priority_actions=priority_actions,
            related_interviews=[iv.get("interview_id", "") for iv in all_interviews],
            confidence=0.9
        )
        
        # 保存反思
        self.reflection_history.append(result)
        self.stats["total_reflections"] += 1
        self.stats["deep_reflections"] += 1
        self.stats["improvements_suggested"] += len(improvement_suggestions)
        
        self._save_reflection(result)
        
        logger.success(f"✅ 深度反思完成: {len(findings)} 项发现, {len(improvement_suggestions)} 条建议")
        return result
    
    # ==================== 分析方法 ====================
    
    def _analyze_question_quality(self, conversation_log: List[Dict]) -> Optional[Dict]:
        """分析提问质量"""
        questions = [
            entry for entry in conversation_log 
            if entry.get("role") == "interviewer" and entry.get("category")
        ]
        
        if not questions:
            return None
        
        # 简单评分：基于问题数量和类别多样性
        categories = set(q.get("category", "") for q in questions)
        diversity_score = min(10, len(categories) * 2)
        
        # 检查是否有追问
        has_followup = any(q.get("type") == "followup" for q in questions)
        followup_bonus = 2 if has_followup else 0
        
        score = min(10, diversity_score + followup_bonus)
        
        return {
            "score": score,
            "details": f"提出 {len(questions)} 个问题，覆盖 {len(categories)} 个类别"
        }
    
    def _analyze_followup_effectiveness(self, conversation_log: List[Dict]) -> Optional[Dict]:
        """分析追问效果"""
        followup_cases = []
        
        # 遍历对话，找到追问及其评估结果
        for i, entry in enumerate(conversation_log):
            if entry.get("type") == "followup":
                question = entry.get("content", "")
                category = entry.get("category", "未知")
                
                # 查找追问后的回答和评估
                answer = ""
                evaluation = ""
                revealed_issue = False
                
                for j in range(i+1, min(i+5, len(conversation_log))):
                    if conversation_log[j].get("role") == "candidate" and not answer:
                        answer = conversation_log[j].get("content", "")
                    elif conversation_log[j].get("role") == "system":
                        evaluation = conversation_log[j].get("content", "")
                        # 检查是否揭示了问题
                        if "露怯" in evaluation or "暴露" in evaluation or "短板" in evaluation:
                            revealed_issue = True
                        break
                
                followup_cases.append({
                    "question": question[:100],  # 限制长度
                    "category": category,
                    "revealed_issue": revealed_issue,
                    "evaluation": evaluation[:200]  # 限制长度
                })
        
        if not followup_cases:
            return {"score": 5, "details": "本次面试未触发追问", "cases": []}
        
        # 统计有效性
        successful_count = sum(1 for case in followup_cases if case["revealed_issue"])
        effectiveness = successful_count / len(followup_cases)
        score = int(effectiveness * 10)
        
        # 生成详细描述
        details_parts = [f"{len(followup_cases)} 次追问，{successful_count} 次有效揭示问题"]
        
        # 添加具体案例
        if successful_count > 0:
            for case in followup_cases:
                if case["revealed_issue"]:
                    details_parts.append(f"  - [{case['category']}] {case['question'][:50]}... → 暴露知识盲区")
        
        return {
            "score": score,
            "details": "\n".join(details_parts),
            "cases": followup_cases
        }
    
    def _analyze_scoring_consistency(self, conversation_log: List[Dict]) -> Optional[Dict]:
        """分析评分一致性"""
        scores = []
        for entry in conversation_log:
            if entry.get("role") == "system" and "评分" in str(entry.get("content", "")):
                content = str(entry.get("content", ""))
                # 尝试提取分数
                try:
                    if "标准化评分:" in content:
                        score_str = content.split("标准化评分:")[1].split("/")[0].strip()
                        scores.append(float(score_str))
                except:
                    pass
        
        if len(scores) < 2:
            return None
        
        # 计算标准差（归一化到0-100）
        std_dev = statistics.stdev(scores)
        # 一致性评分：标准差越小越好
        consistency_score = max(0, 10 - std_dev / 10)
        
        return {
            "score": int(consistency_score),
            "details": f"评分标准差: {std_dev:.1f}，显示{'较好' if std_dev < 15 else '一般'}的一致性"
        }
    
    def _analyze_time_allocation(self, interview_data: Dict) -> Optional[Dict]:
        """分析时间分配"""
        duration = interview_data.get("duration_seconds", 0)
        num_questions = len([
            e for e in interview_data.get("conversation_log", [])
            if e.get("role") == "interviewer" and e.get("category")
        ])
        
        if num_questions == 0:
            return None
        
        avg_time_per_question = duration / num_questions
        
        # 理想时间：每个问题3-5分钟（180-300秒）
        if 180 <= avg_time_per_question <= 300:
            score = 10
            assessment = "合理"
        elif avg_time_per_question < 180:
            score = 7
            assessment = "偏快"
        else:
            score = 7
            assessment = "偏慢"
        
        return {
            "score": score,
            "details": f"平均每题 {avg_time_per_question:.0f} 秒，时间分配{assessment}"
        }
    
    def _identify_recurring_issues(self, interview_batch: List[Dict]) -> List[Dict]:
        """识别重复出现的问题"""
        issue_counter = defaultdict(int)
        
        for interview in interview_batch:
            # 检查immediate reflection的findings
            # 这里简化处理，实际应该分析更多维度
            for entry in interview.get("conversation_log", []):
                if "露怯" in str(entry.get("content", "")):
                    issue_counter["候选人不懂装懂"] += 1
                if "追问" in str(entry.get("type", "")):
                    issue_counter["触发追问"] += 1
        
        # 返回出现3次以上的问题
        recurring = [
            {"issue": k, "count": v} 
            for k, v in issue_counter.items() 
            if v >= 3
        ]
        
        return recurring
    
    def _evaluate_followup_strategy(self, interview_batch: List[Dict]) -> Optional[Dict]:
        """评估追问策略的有效性"""
        total_followups = 0
        successful_followups = 0
        
        for interview in interview_batch:
            for entry in interview.get("conversation_log", []):
                if entry.get("type") == "followup":
                    total_followups += 1
                    if "露怯" in str(entry.get("reason", "")):
                        successful_followups += 1
        
        if total_followups == 0:
            return None
        
        true_positive_rate = successful_followups / total_followups
        false_positive_rate = 1 - true_positive_rate
        
        return {
            "true_positive_rate": true_positive_rate,
            "false_positive_rate": false_positive_rate,
            "summary": f"{total_followups} 次追问中，{successful_followups} 次有效（准确率 {true_positive_rate:.1%}）"
        }
    
    def _analyze_scoring_bias_trend(self, interview_batch: List[Dict]) -> Optional[Dict]:
        """分析评分偏差趋势"""
        all_scores = []
        
        for interview in interview_batch:
            recommendation_score = interview.get("recommendation_score", 0)
            if recommendation_score > 0:
                all_scores.append(recommendation_score)
        
        if not all_scores:
            return None
        
        mean_score = statistics.mean(all_scores)
        
        # 理想均值应该在50左右
        bias = mean_score - 50
        
        if bias > 10:
            direction = "过高（偏宽松）"
        elif bias < -10:
            direction = "过低（偏严格）"
        else:
            direction = "正常"
        
        return {
            "direction": direction,
            "magnitude": abs(bias),
            "details": f"平均推荐分 {mean_score:.1f}，{direction}"
        }
    
    def _extract_lessons_learned(self, interview_batch: List[Dict]) -> Dict:
        """提取经验教训"""
        lessons = {
            "successes": [],
            "failures": []
        }
        
        for interview in interview_batch:
            score = interview.get("recommendation_score", 0)
            
            # 高分案例作为成功经验
            if score >= 75:
                lessons["successes"].append({
                    "interview_id": interview.get("interview_id"),
                    "score": score,
                    "note": "高质量面试"
                })
            # 低分案例作为失败教训
            elif score <= 30:
                lessons["failures"].append({
                    "interview_id": interview.get("interview_id"),
                    "score": score,
                    "note": "需改进的面试"
                })
        
        return lessons
    
    def _review_assessment_framework(self, all_interviews: List[Dict]) -> Optional[Dict]:
        """审查评估框架的合理性"""
        # 简化实现：检查评分分布
        scores = [iv.get("recommendation_score", 0) for iv in all_interviews if iv.get("recommendation_score")]
        
        if not scores:
            return None
        
        mean_score = statistics.mean(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        
        # 理想分布：均值50，标准差15-20
        validity = 10
        if abs(mean_score - 50) > 15:
            validity -= 3
        if std_dev < 10 or std_dev > 30:
            validity -= 2
        
        return {
            "validity": max(0, validity),
            "details": f"评分分布：均值 {mean_score:.1f}，标准差 {std_dev:.1f}"
        }
    
    def _review_core_assumptions(self, all_interviews: List[Dict]) -> Optional[Dict]:
        """检讨核心假设"""
        # 核心假设："使用高级术语但缺乏细节 = 不懂装懂"
        followup_cases = []
        
        for interview in all_interviews:
            for entry in interview.get("conversation_log", []):
                if entry.get("type") == "followup":
                    result = "confirmed" if "露怯" in str(entry) else "refuted"
                    followup_cases.append(result)
        
        if not followup_cases:
            return None
        
        confirmed = followup_cases.count("confirmed")
        total = len(followup_cases)
        confidence = confirmed / total if total > 0 else 0
        
        return {
            "assumptions": ["使用高级术语但缺乏细节 → 不懂装懂"],
            "details": f"该假设在 {total} 次验证中，{confirmed} 次被证实（置信度 {confidence:.1%}）"
        }
    
    def _identify_systematic_bias(self, all_interviews: List[Dict]) -> Optional[Dict]:
        """识别系统性偏见"""
        # 简化实现：检查是否对某类候选人有偏见
        # 实际应该分析候选人特征与评分的相关性
        
        biases = []
        
        # 示例：检查评分分布
        scores = [iv.get("recommendation_score", 0) for iv in all_interviews if iv.get("recommendation_score")]
        if scores:
            mean_score = statistics.mean(scores)
            if mean_score > 60:
                biases.append("可能存在评分偏高的倾向")
            elif mean_score < 40:
                biases.append("可能存在评分偏低的倾向")
        
        return {
            "biases": biases,
            "details": "需要更多数据来确认系统性偏见"
        } if biases else None
    
    # ==================== 洞察和建议生成 ====================
    
    def _generate_insights_from_findings(self, findings: List[Dict]) -> List[str]:
        """从发现中生成洞察"""
        insights = []
        
        concerns = [f for f in findings if f.get("type") == "concern"]
        positives = [f for f in findings if f.get("type") == "positive"]
        
        if concerns:
            insights.append(f"发现 {len(concerns)} 个需要关注的问题")
        if positives:
            insights.append(f"有 {len(positives)} 个方面表现良好")
        
        # 具体洞察
        for finding in findings:
            if finding.get("type") == "concern" and finding.get("score", 0) < 5:
                insights.append(f"{finding.get('dimension')} 需要改进")
        
        return insights
    
    def _generate_improvement_suggestions(self, findings: List[Dict]) -> List[Dict]:
        """生成改进建议"""
        suggestions = []
        
        for finding in findings:
            if finding.get("type") == "concern":
                dimension = finding.get("dimension")
                score = finding.get("score", 0)
                details = finding.get("details", "")
                
                if dimension == "追问效果":
                    # 提取具体案例
                    cases = finding.get("cases", [])
                    
                    if score == 0 and cases:
                        # 追问了但没有揭示问题
                        revealed_cases = [c for c in cases if c["revealed_issue"]]
                        if not revealed_cases:
                            suggestions.append({
                                "dimension": dimension,
                                "action": f"追问策略需要调整：本次追问{len(cases)}次但未有效揭示问题，建议加强追问的深度和针对性",
                                "specific_case": cases[0]["question"][:100] if cases else "",
                                "priority": "high",
                                "expected_impact": "提高追问有效性，减少误判"
                            })
                    elif score < 5:
                        suggestions.append({
                            "dimension": dimension,
                            "action": "优化追问策略，提高追问的针对性",
                            "priority": "high",
                            "expected_impact": "提升追问有效性20%"
                        })
                
                elif dimension == "提问质量" and score < 7:
                    suggestions.append({
                        "dimension": dimension,
                        "action": f"提问覆盖度不足：{details}，建议增加问题数量或扩展类别覆盖",
                        "priority": "medium",
                        "expected_impact": "更全面评估候选人能力"
                    })
                
                elif dimension == "评分一致性" and score < 5:
                    suggestions.append({
                        "dimension": dimension,
                        "action": "建立评分基准，使用历史数据校准",
                        "priority": "medium",
                        "expected_impact": "减少评分波动"
                    })
        
        return suggestions
    
    def _generate_periodic_insights(self, findings: List[Dict], lessons: Dict) -> List[str]:
        """生成阶段性洞察"""
        insights = []
        
        # 从重复问题中提取洞察
        for finding in findings:
            if finding.get("dimension") == "重复问题":
                count = finding.get("count", 0)
                if count > 0:
                    insights.append(f"识别到 {count} 类重复出现的问题，需要系统性改进")
        
        # 从经验教训中提取洞察
        successes = len(lessons.get("successes", []))
        failures = len(lessons.get("failures", []))
        if successes > 0 or failures > 0:
            insights.append(f"成功案例 {successes} 个，需改进案例 {failures} 个")
        
        return insights
    
    def _generate_strategy_adjustments(self, findings: List[Dict], lessons: Dict) -> List[Dict]:
        """生成策略调整方案"""
        suggestions = []
        
        # 基于追问统计调整策略
        for finding in findings:
            if finding.get("dimension") == "追问策略统计":
                tpr = finding.get("true_positive_rate", 0)
                if tpr < 0.5:
                    suggestions.append({
                        "dimension": "追问策略",
                        "action": "降低追问触发阈值，提高召回率",
                        "priority": "high",
                        "expected_impact": "减少漏判"
                    })
                elif tpr > 0.9:
                    suggestions.append({
                        "dimension": "追问策略",
                        "action": "提高追问触发阈值，降低误判",
                        "priority": "medium",
                        "expected_impact": "提高精确率"
                    })
        
        return suggestions
    
    def _generate_deep_insights(self, findings: List[Dict]) -> List[str]:
        """生成深度洞察"""
        insights = []
        
        for finding in findings:
            if finding.get("dimension") == "核心假设检讨":
                details = finding.get("details", "")
                insights.append(f"核心假设验证：{details}")
            
            if finding.get("dimension") == "系统性偏见":
                biases = finding.get("biases", [])
                if biases:
                    insights.append(f"发现系统性偏见：{'; '.join(biases)}")
        
        return insights
    
    def _generate_system_improvements(self, findings: List[Dict]) -> List[Dict]:
        """生成系统级改进建议"""
        suggestions = []
        
        for finding in findings:
            if finding.get("dimension") == "评估框架审查":
                validity = finding.get("validity", 0)
                if validity < 7:
                    suggestions.append({
                        "dimension": "评估框架",
                        "action": "重新设计评分标准，调整权重配置",
                        "priority": "critical",
                        "expected_impact": "提升评估准确性"
                    })
            
            if finding.get("dimension") == "系统性偏见":
                suggestions.append({
                    "dimension": "偏见消除",
                    "action": "引入公平性检查机制，多样化测试案例",
                    "priority": "critical",
                    "expected_impact": "提升评估公平性"
                })
        
        return suggestions
    
    # ==================== 改进应用 ====================
    
    def apply_improvement(self, improvement: Dict) -> bool:
        """
        应用改进建议
        
        Args:
            improvement: 改进建议
            
        Returns:
            是否成功应用
        """
        try:
            # 记录应用
            self.improvements_applied.append({
                **improvement,
                "applied_at": datetime.now().isoformat(),
                "status": "applied"
            })
            
            self.stats["improvements_applied"] += 1
            
            logger.success(f"✅ 应用改进: {improvement.get('action')}")
            return True
        except Exception as e:
            logger.error(f"❌ 应用改进失败: {e}")
            return False
    
    # ==================== 持久化 ====================
    
    def _save_reflection(self, result: ReflectionResult):
        """保存单个反思结果"""
        try:
            filename = f"{result.reflection_id}.json"
            filepath = self.storage_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 反思结果已保存: {filename}")
        except Exception as e:
            logger.error(f"❌ 保存反思失败: {e}")
    
    def save_all(self):
        """保存所有数据"""
        try:
            # 保存统计信息
            stats_file = self.storage_dir / "stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
            
            # 保存改进记录
            improvements_file = self.storage_dir / "improvements.json"
            with open(improvements_file, 'w', encoding='utf-8') as f:
                json.dump(self.improvements_applied, f, ensure_ascii=False, indent=2)
            
            logger.success("💾 反思系统数据已保存")
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")
    
    def _load_reflections(self):
        """加载历史反思"""
        try:
            # 加载统计信息
            stats_file = self.storage_dir / "stats.json"
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            
            # 加载改进记录
            improvements_file = self.storage_dir / "improvements.json"
            if improvements_file.exists():
                with open(improvements_file, 'r', encoding='utf-8') as f:
                    self.improvements_applied = json.load(f)
            
            # 加载所有反思文件
            for filepath in self.storage_dir.glob("*.json"):
                if filepath.name not in ["stats.json", "improvements.json"]:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            reflection = ReflectionResult.from_dict(data)
                            self.reflection_history.append(reflection)
                    except:
                        pass
        
        except Exception as e:
            logger.warning(f"⚠️  加载反思历史失败: {e}")
    
    # ==================== 报告生成 ====================
    
    def generate_reflection_report(self, reflection: ReflectionResult) -> str:
        """
        生成可读的反思报告
        
        Args:
            reflection: 反思结果
            
        Returns:
            格式化的报告文本
        """
        report = []
        report.append("=" * 60)
        report.append(f"🤔 反思报告 - {reflection.reflection_level.upper()}")
        report.append(f"时间: {reflection.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        report.append(f"\n📊 关注领域: {', '.join(reflection.focus_areas)}")
        
        report.append(f"\n🔍 发现 ({len(reflection.findings)} 项):")
        for i, finding in enumerate(reflection.findings, 1):
            report.append(f"\n  {i}. {finding.get('dimension')} [{finding.get('type', 'neutral').upper()}]")
            report.append(f"     {finding.get('details', '')}")
        
        report.append(f"\n💡 洞察 ({len(reflection.insights)} 条):")
        for i, insight in enumerate(reflection.insights, 1):
            report.append(f"  {i}. {insight}")
        
        report.append(f"\n🎯 改进建议 ({len(reflection.improvement_suggestions)} 条):")
        for i, sugg in enumerate(reflection.improvement_suggestions, 1):
            priority = sugg.get('priority', 'medium').upper()
            report.append(f"\n  {i}. [{priority}] {sugg.get('action')}")
            report.append(f"     预期影响: {sugg.get('expected_impact', '未知')}")
        
        if reflection.priority_actions:
            report.append(f"\n⚡ 优先行动项:")
            for i, action in enumerate(reflection.priority_actions, 1):
                report.append(f"  {i}. {action}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
