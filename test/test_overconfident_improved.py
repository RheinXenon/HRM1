"""
测试改进后的面试官对过度自信候选人的追问能力
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import load_candidate_template
from core import InterviewEngine
from loguru import logger

def test_overconfident_candidate():
    """测试过度自信候选人"""
    print("\n" + "="*80)
    print("🔬 测试改进后的面试官 - 过度自信候选人测试")
    print("="*80)
    
    # 加载过度自信候选人配置
    candidate_config = load_candidate_template("overconfident_candidate")
    candidate_name = candidate_config['profile']['name']
    
    print(f"\n📋 候选人: {candidate_name}")
    print(f"   描述: {candidate_config.get('description', '')}")
    
    # 显示知识盲区
    blind_spots = candidate_config['profile'].get('knowledge_blind_spots', {})
    if blind_spots.get('overconfident_areas'):
        print(f"\n⚠️  过度自信领域:")
        for area in blind_spots['overconfident_areas']:
            skill = area['skill']
            actual = area['actual_level']
            perceived = area['perceived_level']
            print(f"   - {skill}: 实际{actual}/10, 自认为{perceived}/10")
    
    print("\n" + "="*80)
    print("🚀 开始面试...")
    print("="*80)
    
    # 创建面试引擎
    engine = InterviewEngine()
    
    # 执行面试（demo模式，3个问题）
    result = engine.run_interview(
        job_file="senior_backend",
        company_file="tech_startup",
        candidate_config=candidate_config,
        mode="demo"  # 快速测试模式
    )
    
    # 分析结果
    print("\n" + "="*80)
    print("📊 测试结果分析")
    print("="*80)
    
    evaluation = result.evaluation
    
    print(f"\n🎯 推荐度评分: {result.recommendation_score}/100")
    print(f"📝 招聘建议: {evaluation.get('recommendation', 'N/A')}")
    
    # 技能评分 (Phase 1: 标准化评分 0-100)
    if "skill_scores" in evaluation:
        print("\n💪 技能评分 (标准化分数):")
        for skill, score in evaluation['skill_scores'].items():
            print(f"   - {skill}: {score}/100")
    
    # 统计追问次数
    followup_count = sum(1 for entry in result.conversation_log 
                        if isinstance(entry, dict) and entry.get('type') == 'followup')
    
    print(f"\n🔍 追问统计:")
    print(f"   - 总追问次数: {followup_count}")
    
    # 检查是否识别出过度自信
    overconfident_detected = False
    for entry in result.conversation_log:
        if isinstance(entry, dict) and 'reason' in entry:
            if '可疑' in entry['reason'] or '追问' in entry.get('type', ''):
                overconfident_detected = True
                print(f"   - 检测到可疑信号: {entry.get('reason', '')}")
    
    print(f"\n✅ 过度自信识别: {'成功' if overconfident_detected else '未检测到'}")
    
    # 评分下降分析
    score_drops = []
    for i, entry in enumerate(result.conversation_log):
        if isinstance(entry, dict) and 'content' in entry:
            content = str(entry['content'])
            if '评分从' in content and '降至' in content:
                score_drops.append(content)
    
    if score_drops:
        print(f"\n📉 评分变化:")
        for drop in score_drops:
            print(f"   {drop}")
    
    # 总结
    if result.summary:
        print(f"\n📄 最终总结:\n{result.summary}")
    
    print("\n" + "="*80)
    print("✅ 测试完成!")
    print("="*80)
    
    # 返回测试结果供分析
    return {
        "recommendation_score": result.recommendation_score,
        "followup_count": followup_count,
        "overconfident_detected": overconfident_detected,
        "score_drops": len(score_drops)
    }

if __name__ == "__main__":
    try:
        result = test_overconfident_candidate()
        
        # 评估改进效果
        print("\n" + "="*80)
        print("🎓 改进效果评估")
        print("="*80)
        
        print(f"\n✅ 追问次数: {result['followup_count']} (期望 >= 1)")
        print(f"✅ 识别过度自信: {result['overconfident_detected']} (期望 True)")
        print(f"✅ 评分下降: {result['score_drops']} (期望 >= 1)")
        
        success_rate = sum([
            result['followup_count'] >= 1,
            result['overconfident_detected'],
            result['score_drops'] >= 1
        ]) / 3 * 100
        
        print(f"\n🎯 成功率: {success_rate:.0f}%")
        
        if success_rate >= 66:
            print("✅ 改进效果良好！")
        else:
            print("⚠️  需要进一步优化")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
