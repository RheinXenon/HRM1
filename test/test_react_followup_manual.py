"""
手动测试React知识盲区追问
通过交互式问答验证修复效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """手动测试主函数"""
    # 延迟导入避免循环依赖
    from config import load_candidate_template
    from core.llm_client import LLMClient
    from agents.candidate_agent import CandidateAgent
    from agents.interviewer_agent import InterviewerAgent
    
    print("\n" + "=" * 80)
    print("🔍 React知识盲区追问测试")
    print("=" * 80)
    print()
    
    # 加载测试候选人
    candidate_config = load_candidate_template("test_react_blind_spot")
    from agents.candidate_agent import CandidateProfile
    profile = CandidateProfile(**candidate_config['profile'])
    
    print(f"📋 候选人: {profile.name}")
    print(f"   React 技能: actual_level=3/10, perceived_level=7/10")
    p = profile.personality
    print(f"   人格特质: C={p.get('conscientiousness', 0.5):.2f}, N={p.get('neuroticism', 0.5):.2f}")
    print()
    
    # 创建Agent
    from config import load_job_config, load_company_config
    job_config = load_job_config("senior_backend")
    company_config = load_company_config("tech_startup")
    
    llm_client = LLMClient()
    candidate = CandidateAgent(llm_client, profile)
    interviewer = InterviewerAgent(llm_client, job_config, company_config)
    
    # 第一轮：初始问题
    print("-" * 80)
    print("【第一轮】初始问题 - 涉及知识盲区")
    print("-" * 80)
    
    question1 = "请谈谈你对React Hooks的理解和使用经验，特别是useEffect的使用场景。"
    print(f"\n👔 面试官: {question1}\n")
    
    answer1 = candidate.answer_question(
        question=question1,
        question_context={
            "category": "技术能力",
            "expected_skills": ["react"],
            "is_followup": False
        }
    )
    print(f"👤 候选人: {answer1}\n")
    
    eval1 = interviewer.evaluate_answer(
        question=question1,
        answer=answer1,
        target_skills=["react"]
    )
    
    print(f"📊 初始评分: {eval1['normalized_score']:.1f}/100")
    print(f"   信心水平: {eval1['confidence_level']}")
    print()
    
    # 第二轮：深入追问
    print("-" * 80)
    print("【第二轮】深入追问 - 测试是否会'圆过去'")
    print("-" * 80)
    
    question2 = "你提到useEffect，能具体说说依赖数组的工作原理吗？比如为什么空数组只在mount时执行一次？如果依赖是对象或数组会遇到什么问题？cleanup函数的执行时机是什么？"
    print(f"\n👔 面试官: {question2}\n")
    
    answer2 = candidate.answer_question(
        question=question2,
        question_context={
            "category": "技术能力",
            "expected_skills": ["react"],
            "is_followup": True  # 关键：标记为追问
        }
    )
    print(f"👤 候选人: {answer2}\n")
    
    eval2 = interviewer.evaluate_answer(
        question=question2,
        answer=answer2,
        target_skills=["react"]
    )
    
    print(f"📊 追问评分: {eval2['normalized_score']:.1f}/100")
    print(f"   信心水平: {eval2['confidence_level']}")
    print()
    
    # 分析结果
    print("=" * 80)
    print("📊 测试结果分析")
    print("=" * 80)
    
    score_drop = eval1['normalized_score'] - eval2['normalized_score']
    print(f"\n评分变化: {eval1['normalized_score']:.1f} → {eval2['normalized_score']:.1f} (下降: {score_drop:.1f}分)")
    
    # 检查是否包含不应该知道的高级术语
    print(f"\n术语检查 (actual_level=3的候选人不应该知道这些):")
    forbidden_terms = [
        ("依赖数组", "dependency array"),
        ("浅比较", "shallow compare", "Object.is"),
        ("useRef", "useCallback", "useMemo"),
        ("cleanup", "清理函数"),
        ("闭包陷阱", "stale closure"),
        ("比较算法", "reconciliation")
    ]
    
    found_forbidden = []
    for terms in forbidden_terms:
        if isinstance(terms, tuple):
            for term in terms:
                if term.lower() in answer2.lower():
                    found_forbidden.append(term)
                    print(f"   ❌ 发现: '{term}'")
                    break
    
    if not found_forbidden:
        print(f"   ✅ 未发现超出能力的术语")
    
    # 检查露怯信号
    print(f"\n露怯信号检查:")
    weakness_indicators = [
        "记不太清", "不太记得", "记不清楚", "不太熟", "不太确定",
        "了解不够深入", "不太了解", "好像", "应该是", "可能是",
        "我不清楚", "我忘了", "这块我", "没深入研究"
    ]
    
    found_weakness = [w for w in weakness_indicators if w in answer2]
    
    if found_weakness:
        print(f"   ✅ 检测到露怯: {', '.join(found_weakness[:3])}")
    else:
        print(f"   ❌ 未检测到露怯信号")
    
    # 最终判断
    print(f"\n" + "=" * 80)
    print(f"最终判断:")
    print(f"=" * 80)
    
    issues = []
    
    if found_forbidden:
        issues.append(f"❌ 说出了{len(found_forbidden)}个超出能力的正确术语")
    
    if not found_weakness:
        issues.append(f"❌ 没有表现出知识不足的露怯信号")
    
    if score_drop < 10:
        issues.append(f"❌ 评分下降不明显 (仅{score_drop:.1f}分)")
    
    if issues:
        print(f"\n⚠️  发现问题:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n   这说明候选人在'圆过去'，修复可能未完全生效")
    else:
        print(f"\n✅ 测试通过!")
        print(f"   - 候选人没有说出超出能力的术语")
        print(f"   - 候选人表现出了知识不足")
        print(f"   - 评分合理下降")
        print(f"\n   候选人正确地表现出了actual_level=3的知识边界")
    
    print()


if __name__ == "__main__":
    main()
