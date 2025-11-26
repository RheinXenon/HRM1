"""
候选人回答分析器（模拟未来接入的AI模型）

这是一个模拟器，模拟两个真实的AI分析模型：
1. 大五人格预测模型
2. 谎言/夸大检测模型

核心原理：
- Ground Truth：候选人配置中的 personality 和 knowledge_blind_spots
- 正常情况：输出接近 Ground Truth + 小波动（模拟模型不准确性）
- 偏移情况：当候选人在某问题上"不懂装懂"或"过度谦虚"时，产生明显偏移
"""

import random
from typing import Dict, List, Optional
from loguru import logger


class CandidateAnalyzer:
    """候选人回答分析器（模拟器）"""
    
    def __init__(self, noise_level: float = 0.05):
        """
        初始化分析器
        
        Args:
            noise_level: 正常波动程度（0-1），模拟真实模型的测量误差
        """
        self.noise_level = noise_level
        
    def analyze_answer(
        self, 
        answer: str, 
        question: str = None,
        target_skills: List[str] = None,
        candidate_profile: Dict = None
    ) -> Dict:
        """
        分析候选人回答
        
        Args:
            answer: 候选人的回答内容
            question: 问题内容（可选）
            target_skills: 问题涉及的技能列表（可选）
            candidate_profile: 候选人档案（必需，包含 personality 和 knowledge_blind_spots）
            
        Returns:
            包含大五人格和谎言检测结果的字典
        """
        if not candidate_profile:
            logger.warning("⚠️  未提供候选人档案，无法进行分析")
            return self._get_default_result()
        
        # 提取 Ground Truth
        true_personality = candidate_profile.get("personality", {})
        knowledge_blind_spots = candidate_profile.get("knowledge_blind_spots", {})
        
        # 判断当前回答是否涉及"知识盲区"
        blind_spot_context = self._detect_blind_spot_context(
            target_skills=target_skills,
            knowledge_blind_spots=knowledge_blind_spots,
            candidate_skills=candidate_profile.get("skills", {})
        )
        
        # 1. 大五人格预测（基于 Ground Truth + 偏移）
        personality_scores = self._predict_personality(
            true_personality=true_personality,
            blind_spot_context=blind_spot_context
        )
        
        # 2. 谎言/夸大检测
        deception_confidence = self._detect_deception(
            blind_spot_context=blind_spot_context
        )
        
        return {
            "personality_prediction": personality_scores,
            "deception_detection": deception_confidence,
            "blind_spot_triggered": blind_spot_context["triggered"]
        }
    
    def _detect_blind_spot_context(
        self,
        target_skills: List[str],
        knowledge_blind_spots: Dict,
        candidate_skills: Dict[str, int]
    ) -> Dict:
        """
        检测当前回答是否涉及候选人的知识盲区
        
        Returns:
            {
                "triggered": bool,  # 是否触发知识盲区
                "type": str,  # "overconfident" 或 "underconfident" 或 None
                "intensity": float,  # 盲区强度 (0-1)
                "skill": str  # 涉及的技能
            }
        """
        if not target_skills or not knowledge_blind_spots:
            return {"triggered": False, "type": None, "intensity": 0.0, "skill": None}
        
        # 检查过度自信领域
        overconfident_areas = knowledge_blind_spots.get("overconfident_areas", [])
        for area in overconfident_areas:
            skill = area.get("skill", "")
            # 检查是否匹配（模糊匹配）
            for target_skill in target_skills:
                if skill.lower() in target_skill.lower() or target_skill.lower() in skill.lower():
                    actual_level = area.get("actual_level", 5)
                    perceived_level = area.get("perceived_level", 5)
                    gap = perceived_level - actual_level
                    
                    # 计算盲区强度（归一化到 0-1）
                    intensity = min(1.0, gap / 10.0)
                    
                    return {
                        "triggered": True,
                        "type": "overconfident",
                        "intensity": intensity,
                        "skill": skill,
                        "actual_level": actual_level,
                        "perceived_level": perceived_level
                    }
        
        # 检查过度谦虚领域
        underconfident_areas = knowledge_blind_spots.get("underconfident_areas", [])
        for area in underconfident_areas:
            skill = area.get("skill", "")
            for target_skill in target_skills:
                if skill.lower() in target_skill.lower() or target_skill.lower() in skill.lower():
                    actual_level = area.get("actual_level", 5)
                    perceived_level = area.get("perceived_level", 5)
                    gap = actual_level - perceived_level
                    
                    intensity = min(1.0, gap / 10.0)
                    
                    return {
                        "triggered": True,
                        "type": "underconfident",
                        "intensity": intensity,
                        "skill": skill,
                        "actual_level": actual_level,
                        "perceived_level": perceived_level
                    }
        
        return {"triggered": False, "type": None, "intensity": 0.0, "skill": None}
    
    def _predict_personality(
        self,
        true_personality: Dict[str, float],
        blind_spot_context: Dict
    ) -> Dict[str, float]:
        """
        预测大五人格（基于 Ground Truth + 盲区偏移）
        
        Args:
            true_personality: 真实的大五人格（Ground Truth）
            blind_spot_context: 知识盲区上下文
            
        Returns:
            预测的大五人格分数
        """
        # 默认值
        default_personality = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }
        
        # 使用真实性格或默认值
        base_scores = {}
        for key in default_personality.keys():
            base_scores[key] = true_personality.get(key, default_personality[key])
        
        # 正常情况：只有小波动
        predicted_scores = {}
        for key, value in base_scores.items():
            noise = random.uniform(-self.noise_level, self.noise_level)
            predicted_scores[key] = max(0.0, min(1.0, value + noise))
        
        # 如果触发知识盲区，产生偏移
        if blind_spot_context["triggered"]:
            intensity = blind_spot_context["intensity"]
            blind_type = blind_spot_context["type"]
            
            if blind_type == "overconfident":
                # 过度自信时：
                # - 神经质降低（表现得更自信，不焦虑）
                # - 尽责性可能降低（不够仔细审视自己的能力）
                predicted_scores["neuroticism"] = max(
                    0.0,
                    predicted_scores["neuroticism"] - intensity * 0.3
                )
                predicted_scores["conscientiousness"] = max(
                    0.0,
                    predicted_scores["conscientiousness"] - intensity * 0.2
                )
                
            elif blind_type == "underconfident":
                # 过度谦虚时：
                # - 神经质升高（更焦虑、不确定）
                # - 宜人性可能升高（过于谦虚礼貌）
                predicted_scores["neuroticism"] = min(
                    1.0,
                    predicted_scores["neuroticism"] + intensity * 0.3
                )
                predicted_scores["agreeableness"] = min(
                    1.0,
                    predicted_scores["agreeableness"] + intensity * 0.2
                )
        
        return predicted_scores
    
    def _detect_deception(
        self,
        blind_spot_context: Dict
    ) -> Dict[str, float]:
        """
        检测谎言/夸大（基于知识盲区）
        
        真实谎言检测模型的特点：
        - 诚实时：置信度极低（0-0.1）
        - 明显撒谎时：置信度极高（0.75-0.95）
        - 中间值很少出现
        
        Args:
            blind_spot_context: 知识盲区上下文
            
        Returns:
            谎言检测结果
        """
        if not blind_spot_context["triggered"]:
            # 没有触发知识盲区 -> 诚实回答
            # 置信度应该极低（0-0.1），模拟真实模型对诚实回答的判断
            confidence = random.uniform(0.0, 0.08)
            
            # 添加小噪声
            confidence += random.uniform(-self.noise_level/2, self.noise_level/2)
            confidence = max(0.0, min(0.15, confidence))  # 限制在0-0.15
            
            level = "低"
            interpretation = "回答真实可信"
            
            return {
                "confidence": confidence,
                "level": level,
                "interpretation": interpretation,
                "triggered_by": None
            }
        
        # 触发了知识盲区
        blind_type = blind_spot_context["type"]
        intensity = blind_spot_context["intensity"]
        skill = blind_spot_context["skill"]
        
        if blind_type == "overconfident":
            # 过度自信（不懂装懂）-> 明显撒谎/夸大
            # 置信度应该极高（0.7-0.95），根据盲区强度调整
            
            # 基础高置信度：0.65 + intensity * 0.25
            # intensity在0-1之间，所以最终在0.65-0.90
            base_high = 0.65 + intensity * 0.25
            
            # 添加噪声（±5%）
            confidence = base_high + random.uniform(-0.05, 0.05)
            confidence = max(0.65, min(0.98, confidence))  # 限制在0.65-0.98
            
            # 分级更明确
            if confidence >= 0.85:
                level = "极高"
                interpretation = f"强烈怀疑夸大或撒谎（涉及{skill}）"
            elif confidence >= 0.70:
                level = "高"
                interpretation = f"可能存在明显夸大（涉及{skill}）"
            else:
                level = "中-高"
                interpretation = f"存在夸大倾向（涉及{skill}）"
            
            return {
                "confidence": confidence,
                "level": level,
                "interpretation": interpretation,
                "triggered_by": "overconfident",
                "skill": skill,
                "intensity": intensity
            }
        
        elif blind_type == "underconfident":
            # 过度谦虚 -> 隐藏能力（不是撒谎，只是保守）
            # 置信度应该略微升高但仍然较低（0.1-0.3）
            
            base_low = 0.08 + intensity * 0.2  # 0.08-0.28
            confidence = base_low + random.uniform(-0.03, 0.03)
            confidence = max(0.05, min(0.35, confidence))  # 限制在0.05-0.35
            
            if confidence >= 0.25:
                level = "中-低"
                interpretation = f"回答可能过于保守，未充分展示能力（涉及{skill}）"
            else:
                level = "低"
                interpretation = f"回答真实但保守（涉及{skill}）"
            
            return {
                "confidence": confidence,
                "level": level,
                "interpretation": interpretation,
                "triggered_by": "underconfident",
                "skill": skill,
                "intensity": intensity
            }
        
        # 理论上不会到这里
        return {
            "confidence": random.uniform(0.0, 0.08),
            "level": "低",
            "interpretation": "未知情况",
            "triggered_by": None
        }
    
    def _get_default_result(self) -> Dict:
        """返回默认结果（当无法分析时）"""
        return {
            "personality_prediction": {
                "openness": 0.5,
                "conscientiousness": 0.5,
                "extraversion": 0.5,
                "agreeableness": 0.5,
                "neuroticism": 0.5
            },
            "deception_detection": {
                "confidence": 0.1,
                "level": "低",
                "interpretation": "无法分析",
                "triggered_by": None
            },
            "blind_spot_triggered": False
        }
    
    @staticmethod
    def format_analysis_result(analysis_result: Dict) -> str:
        """
        格式化分析结果为可读文本
        
        Args:
            analysis_result: analyze_answer返回的结果
            
        Returns:
            格式化的文本
        """
        personality = analysis_result["personality_prediction"]
        deception = analysis_result["deception_detection"]
        
        # 大五人格维度名称
        personality_names = {
            "openness": "开放性",
            "conscientiousness": "尽责性",
            "extraversion": "外向性",
            "agreeableness": "宜人性",
            "neuroticism": "神经质"
        }
        
        # 格式化输出
        lines = []
        lines.append("📊 【候选人回答分析】")
        lines.append("")
        lines.append("🧠 大五人格预测:")
        for key, value in personality.items():
            name = personality_names.get(key, key)
            bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            lines.append(f"   {name:6s} [{bar}] {value:.2f}")
        
        lines.append("")
        lines.append("🔍 谎言/夸大检测:")
        lines.append(f"   置信度: {deception['confidence']:.2f} ({deception['level']})")
        lines.append(f"   解读: {deception['interpretation']}")
        
        # 如果触发了知识盲区，显示额外信息
        if analysis_result.get("blind_spot_triggered"):
            triggered_by = deception.get("triggered_by")
            if triggered_by:
                skill = deception.get("skill", "未知")
                intensity = deception.get("intensity", 0)
                lines.append(f"   ⚠️  触发知识盲区: {skill} (强度: {intensity:.2f})")
        
        return "\n".join(lines)


def test_analyzer():
    """测试分析器"""
    print("=" * 70)
    print("候选人回答分析器测试（基于 Ground Truth 的模拟器）")
    print("=" * 70)
    
    analyzer = CandidateAnalyzer(noise_level=0.05)
    
    # 测试案例1: 正常情况（无知识盲区）
    print("\n【测试1: 正常回答，无知识盲区】")
    print("-" * 70)
    normal_profile = {
        "personality": {
            "openness": 0.65,
            "conscientiousness": 0.70,
            "extraversion": 0.55,
            "agreeableness": 0.60,
            "neuroticism": 0.40
        },
        "knowledge_blind_spots": {
            "overconfident_areas": [],
            "underconfident_areas": []
        },
        "skills": {"Python": 8}
    }
    
    result = analyzer.analyze_answer(
        answer="我在项目中使用了Python进行数据分析...",
        target_skills=["Python"],
        candidate_profile=normal_profile
    )
    print(CandidateAnalyzer.format_analysis_result(result))
    
    # 测试案例2: 过度自信（不懂装懂）
    print("\n\n【测试2: 过度自信 - 回答涉及知识盲区】")
    print("-" * 70)
    overconfident_profile = {
        "personality": {
            "openness": 0.60,
            "conscientiousness": 0.50,
            "extraversion": 0.70,
            "agreeableness": 0.55,
            "neuroticism": 0.30  # 低神经质，容易自信
        },
        "knowledge_blind_spots": {
            "overconfident_areas": [
                {
                    "skill": "React",
                    "actual_level": 3,  # 实际只懂基础
                    "perceived_level": 7,  # 自以为很懂
                    "description": "只学过基础教程，但自认为能做复杂项目"
                }
            ],
            "underconfident_areas": []
        },
        "skills": {"React": 3}
    }
    
    result = analyzer.analyze_answer(
        answer="关于React的性能优化，我认为...",
        target_skills=["React"],
        candidate_profile=overconfident_profile
    )
    print(CandidateAnalyzer.format_analysis_result(result))
    print(f"\n分析: 由于候选人在React上过度自信（实际3/10，自认为7/10），")
    print(f"      模型检测到较高的谎言置信度，且神经质降低（表现得过于自信）")
    
    # 测试案例3: 过度谦虚
    print("\n\n【测试3: 过度谦虚 - 低估自己能力】")
    print("-" * 70)
    underconfident_profile = {
        "personality": {
            "openness": 0.55,
            "conscientiousness": 0.75,
            "extraversion": 0.45,
            "agreeableness": 0.70,
            "neuroticism": 0.65  # 高神经质，容易焦虑
        },
        "knowledge_blind_spots": {
            "overconfident_areas": [],
            "underconfident_areas": [
                {
                    "skill": "数据库",
                    "actual_level": 8,  # 实际很强
                    "perceived_level": 5,  # 自认为一般
                    "description": "有丰富经验但总觉得自己还差得远"
                }
            ]
        },
        "skills": {"数据库": 8}
    }
    
    result = analyzer.analyze_answer(
        answer="关于数据库优化，我了解一些...",
        target_skills=["数据库"],
        candidate_profile=underconfident_profile
    )
    print(CandidateAnalyzer.format_analysis_result(result))
    print(f"\n分析: 由于候选人在数据库上过度谦虚（实际8/10，自认为5/10），")
    print(f"      模型检测到中等置信度（过于保守），且神经质升高（表现得焦虑）")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)


if __name__ == "__main__":
    test_analyzer()
