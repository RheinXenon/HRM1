"""
专门测试知识盲区追问机制
验证候选人在知识盲区被追问时是否会"圆过去"
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataclasses import dataclass
from typing import Dict, Any
from loguru import logger

# 延迟导入避免循环依赖
def get_agents():
    from agents.candidate_agent import CandidateAgent, CandidateProfile
    from agents.interviewer_agent import InterviewerAgent
    from core.llm_client import LLMClient
    return CandidateAgent, CandidateProfile, InterviewerAgent, LLMClient


def test_blind_spot_followup():
    """测试知识盲区被追问时的表现"""
    
    # 延迟导入
    CandidateAgent, CandidateProfile, InterviewerAgent, LLMClient = get_agents()
    
    print("\n" + "=" * 80)
    print("🔍 知识盲区追问测试")
    print("=" * 80)
    print()
    
    # 创建一个过度自信的候选人配置
    # React能力: actual=3, perceived=7
    candidate_profile = CandidateProfile(
        name="测试候选人",
        skills={
            "react": 3,  # 实际能力很低
            "python": 7,
            "sql": 6
        },
        experience={
            "years": 3,
            "level": "mid",
            "projects": [
                {
                    "name": "简单网站",
                    "role": "开发",
                    "achievement": "完成基础功能"
                }
            ]
        },
        personality={
            "openness": 0.65,
            "conscientiousness": 0.40,  # 低尽责性
            "extraversion": 0.75,
            "agreeableness": 0.50,
            "neuroticism": 0.25  # 低神经质 -> 容易过度自信
        },
        knowledge_blind_spots={
            "overconfident_areas": [
                {
                    "skill": "react",
                    "actual_level": 3,
                    "perceived_level": 7,
                    "description": "只做过简单的React项目，但会过度自信地谈论hooks、性能优化等高级话题"
                }
            ],
            "underconfident_areas": []
        }
    )
    
    print(f"📋 候选人: {candidate_profile.name}")
    print(f"   React 技能: actual_level={candidate_profile.knowledge_blind_spots['overconfident_areas'][0]['actual_level']}/10")
    print(f"   人格特质: 尽责性={candidate_profile.personality['conscientiousness']:.2f}, 神经质={candidate_profile.personality['neuroticism']:.2f}")
    print(f"   倾向: 低尽责性+低神经质 -> 容易过度自信")
    print()
    
    # 创建LLM客户端和Agent
    llm_client = LLMClient()
    candidate = CandidateAgent(llm_client, candidate_profile)
    interviewer = InterviewerAgent(llm_client)
    
    # 第一轮：初始问题
    print("-" * 80)
    print("【第一轮】初始问题 - 涉及知识盲区")
    print("-" * 80)
    
    initial_question = "请谈谈你对React Hooks的理解和使用经验，特别是useEffect的使用场景和注意事项。"
    print(f"\n👔 面试官: {initial_question}\n")
    
    initial_answer = candidate.answer_question(
        question=initial_question,
        question_context={
            "category": "技术能力",
            "expected_skills": ["react"],
            "is_followup": False
        }
    )
    print(f"👤 候选人: {initial_answer}\n")
    
    # 评估初始回答
    initial_eval = interviewer.evaluate_answer(
        question=initial_question,
        answer=initial_answer,
        target_skills=["react"]
    )
    
    print(f"📊 初始评分: {initial_eval['normalized_score']:.1f}/100")
    print(f"   信心水平: {initial_eval['confidence_level']}")
    print(f"   需要追问: {initial_eval['need_follow_up']}")
    print()
    
    # 第二轮：深入追问
    print("-" * 80)
    print("【第二轮】深入追问 - 测试是否会'圆过去'")
    print("-" * 80)
    
    followup_question = "你提到useEffect，能具体说说依赖数组的工作原理吗？比如为什么空数组只在mount时执行一次？如果依赖是对象或数组，会遇到什么问题？还有cleanup函数的执行时机是什么？"
    print(f"\n👔 面试官: {followup_question}\n")
    
    followup_answer = candidate.answer_question(
        question=followup_question,
        question_context={
            "category": "技术能力",
            "expected_skills": ["react"],
            "is_followup": True  # 标记为追问
        }
    )
    print(f"👤 候选人: {followup_answer}\n")
    
    # 评估追问回答
    followup_eval = interviewer.evaluate_answer(
        question=followup_question,
        answer=followup_answer,
        target_skills=["react"]
    )
    
    print(f"📊 追问评分: {followup_eval['normalized_score']:.1f}/100")
    print(f"   信心水平: {followup_eval['confidence_level']}")
    print()
    
    # 分析结果
    print("=" * 80)
    print("📊 分析结果")
    print("=" * 80)
    
    score_drop = initial_eval['normalized_score'] - followup_eval['normalized_score']
    print(f"\n评分变化: {initial_eval['normalized_score']:.1f} → {followup_eval['normalized_score']:.1f} (差值: {score_drop:.1f})")
    
    # 检查是否包含不应该知道的高级术语
    forbidden_terms = [
        "依赖数组", "dependency array", "浅比较", "shallow compare",
        "useRef", "cleanup", "unmount", "Object.is", "闭包陷阱"
    ]
    
    found_forbidden = []
    for term in forbidden_terms:
        if term.lower() in followup_answer.lower():
            found_forbidden.append(term)
    
    print(f"\n术语检查:")
    if found_forbidden:
        print(f"   ❌ 发现超出能力范围的正确术语: {', '.join(found_forbidden)}")
        print(f"   ⚠️  候选人actual_level=3，不应该知道这些高级概念！")
    else:
        print(f"   ✅ 未发现超出能力范围的术语")
    
    # 检查是否露怯
    weakness_indicators = [
        "记不太清", "不太记得", "记不清楚", "不太熟",
        "不太确定", "了解不够深入", "不太了解", "好像", "应该是"
    ]
    
    found_weakness = []
    for indicator in weakness_indicators:
        if indicator in followup_answer:
            found_weakness.append(indicator)
    
    print(f"\n露怯检查:")
    if found_weakness:
        print(f"   ✅ 检测到露怯信号: {', '.join(found_weakness)}")
    else:
        print(f"   ❌ 未检测到露怯信号（可能在'圆过去'）")
    
    # 最终判断
    print(f"\n最终判断:")
    if score_drop >= 20:
        print(f"   ✅ 追问后评分显著下降，成功识别不懂装懂")
    elif found_forbidden and not found_weakness:
        print(f"   ❌ 问题：候选人说出了超出能力的正确术语，但没有露怯")
        print(f"   ⚠️  这说明候选人在'圆过去'，修复未完全生效")
    elif found_weakness and not found_forbidden:
        print(f"   ✅ 候选人正确地表现出知识不足，没有'圆过去'")
    else:
        print(f"   ⚡ 结果不明确，需要人工检查回答内容")
    
    print()


def main():
    """主函数"""
    print("\n")
    print("🧪" * 40)
    print("知识盲区追问机制专项测试")
    print("🧪" * 40)
    
    test_blind_spot_followup()
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
