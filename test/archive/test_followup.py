"""
测试追问机制
专门测试过度自信候选人是否会被追问并暴露不懂装懂
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径（从test文件夹向上一级）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import load_candidate_template
from core import InterviewEngine
from loguru import logger


def test_overconfident_with_followup():
    """测试过度自信候选人的追问效果"""
    
    print("\n" + "=" * 80)
    print("🔍 追问机制测试 - 过度自信候选人")
    print("=" * 80)
    print()
    
    # 加载过度自信候选人
    candidate_config = load_candidate_template("overconfident_candidate")
    profile = candidate_config['profile']
    
    print(f"📋 候选人: {profile['name']}")
    p = profile['personality']
    print(f"   人格特质: C={p.get('conscientiousness', 0.5):.2f}, N={p.get('neuroticism', 0.5):.2f}")
    print()
    
    print("🔴 知识盲区:")
    for area in profile['knowledge_blind_spots']['overconfident_areas']:
        print(f"   • {area['skill']}: 实际{area['actual_level']}/10 → 自我感觉{area['perceived_level']}/10")
    print()
    
    print("-" * 80)
    print("🚀 开始面试（demo模式，3个问题）...")
    print("-" * 80)
    print()
    
    # 创建面试引擎
    engine = InterviewEngine()
    
    # 执行面试
    result = engine.run_interview(
        job_file="senior_backend",
        company_file="tech_startup",
        candidate_config=candidate_config,
        mode="demo"
    )
    
    # 分析结果
    print("\n" + "=" * 80)
    print("📊 追问机制分析")
    print("=" * 80)
    
    # 统计追问次数
    followup_count = 0
    exposed_count = 0
    
    for msg in result.conversation_log:
        if msg.get("type") == "followup":
            followup_count += 1
            print(f"\n🔍 追问 #{followup_count}:")
            print(f"   原因: {msg.get('reason', '未知')}")
            print(f"   问题: {msg.get('content', '')[:100]}...")
        
        if "追问后露怯" in msg.get("content", ""):
            exposed_count += 1
            print(f"\n🚩 检测到不懂装懂！")
            print(f"   {msg.get('content', '')}")
    
    print(f"\n📈 统计:")
    print(f"   追问次数: {followup_count}")
    print(f"   暴露次数: {exposed_count}")
    print(f"   最终推荐度: {result.recommendation_score}/100")
    
    if followup_count > 0:
        print("\n✅ 追问机制已触发!")
        if exposed_count > 0:
            print("✅ 成功识别出不懂装懂!")
        else:
            print("⚠️  追问了但未暴露，可能需要调整检测阈值")
    else:
        print("\n⚠️  未触发追问机制")
        print("   可能原因:")
        print("   1. 候选人回答没有触发可疑信号（太详细或没有高级术语）")
        print("   2. 评分不够高（需要>=7才会追问）")
        print("   3. 检测阈值需要调整")


def main():
    """主函数"""
    print("\n")
    print("🧪" * 40)
    print("追问机制功能测试")
    print("🧪" * 40)
    
    test_overconfident_with_followup()
    
    print("\n\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
