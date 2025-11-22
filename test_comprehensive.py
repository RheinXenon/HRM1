"""
全面测试：对比不同类型候选人的面试效果
验证改进后的追问机制能否有效区分真实水平
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import load_candidate_template
from core import InterviewEngine
from loguru import logger

def test_candidate(template_name, description):
    """测试单个候选人"""
    print(f"\n{'='*80}")
    print(f"🎯 测试候选人: {description}")
    print(f"{'='*80}")
    
    # 加载配置
    candidate_config = load_candidate_template(template_name)
    candidate_name = candidate_config['profile']['name']
    
    # 创建面试引擎
    engine = InterviewEngine()
    
    # 执行面试
    result = engine.run_interview(
        job_file="senior_backend",
        company_file="tech_startup",
        candidate_config=candidate_config,
        mode="demo"
    )
    
    # 统计追问
    followup_count = sum(1 for entry in result.conversation_log 
                        if isinstance(entry, dict) and entry.get('type') == 'followup')
    
    # 统计评分变化
    score_changes = []
    for entry in result.conversation_log:
        if isinstance(entry, dict) and 'content' in entry:
            content = str(entry['content'])
            if '追问评分' in content:
                score_changes.append(content)
    
    # 检测过度自信
    overconfident = result.evaluation.get('overconfidence_detected', False)
    
    return {
        "name": candidate_name,
        "template": template_name,
        "recommendation_score": result.recommendation_score,
        "recommendation": result.evaluation.get('recommendation', 'N/A'),
        "followup_count": followup_count,
        "overconfident_detected": overconfident,
        "score_changes": score_changes,
        "skill_scores": result.evaluation.get('skill_scores', {}),
        "summary": result.summary[:100] + "..." if len(result.summary) > 100 else result.summary
    }

def main():
    """运行全面对比测试"""
    print("\n" + "="*80)
    print("🔬 全面测试：改进后的追问机制效果验证")
    print("="*80)
    
    # 测试不同类型的候选人
    test_cases = [
        ("ideal_candidate", "理想候选人（真才实学）"),
        ("overconfident_candidate", "过度自信候选人（不懂装懂）"),
        ("junior_candidate", "初级候选人（能力不足但诚实）"),
    ]
    
    results = []
    
    for template, desc in test_cases:
        try:
            result = test_candidate(template, desc)
            results.append(result)
            
            # 简要输出
            print(f"\n✅ {result['name']}: 推荐度 {result['recommendation_score']}/100, "
                  f"建议={result['recommendation']}, "
                  f"追问={result['followup_count']}次, "
                  f"过度自信={result['overconfident_detected']}")
            
        except Exception as e:
            logger.error(f"❌ 测试 {desc} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 生成对比报告
    print("\n" + "="*80)
    print("📊 对比分析报告")
    print("="*80)
    
    print(f"\n{'候选人':<15} {'推荐度':<10} {'建议':<10} {'追问次数':<10} {'过度自信':<10}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['name']:<15} {r['recommendation_score']:<10} "
              f"{r['recommendation']:<10} {r['followup_count']:<10} "
              f"{'是' if r['overconfident_detected'] else '否':<10}")
    
    # 验证期望结果
    print("\n" + "="*80)
    print("✅ 期望验证")
    print("="*80)
    
    expectations = {
        "理想候选人应该得分高": results[0]['recommendation_score'] >= 80 if results else False,
        "过度自信候选人应该被识别": results[1]['overconfident_detected'] if len(results) > 1 else False,
        "过度自信候选人评分应降低": results[1]['recommendation_score'] < 75 if len(results) > 1 else False,
        "理想候选人和过度自信者评分应有差异": abs(results[0]['recommendation_score'] - results[1]['recommendation_score']) >= 15 if len(results) > 1 else False
    }
    
    for expectation, passed in expectations.items():
        status = "✅" if passed else "❌"
        print(f"{status} {expectation}: {passed}")
    
    success_rate = sum(expectations.values()) / len(expectations) * 100
    print(f"\n🎯 总体成功率: {success_rate:.0f}%")
    
    if success_rate >= 75:
        print("\n🎉 改进效果优秀！面试官能有效识别过度自信候选人！")
    elif success_rate >= 50:
        print("\n✅ 改进效果良好，但仍有优化空间")
    else:
        print("\n⚠️  改进效果有限，需要进一步优化")
    
    # 保存详细结果
    output_file = Path("data/analysis/comprehensive_test_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "results": results,
            "expectations": {k: v for k, v in expectations.items()},
            "success_rate": success_rate
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细结果已保存至: {output_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
