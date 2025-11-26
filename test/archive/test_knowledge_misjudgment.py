"""
测试知识误判功能（基于大五人格模型）
演示过度自信（不懂装懂）和过度谦虚（低估能力）的效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.personality_generator import PersonalityGenerator
import json


def demonstrate_personality_patterns():
    """展示不同大五人格组合的知识误判倾向"""
    print("=" * 80)
    print("🧠 大五人格与知识误判倾向对比测试")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "label": "过度自信型 (不懂装懂)",
            "personality": {
                "openness": 0.65,
                "conscientiousness": 0.35,  # 低尽责性
                "extraversion": 0.75,
                "agreeableness": 0.45,
                "neuroticism": 0.25  # 低神经质
            },
            "tendency": "overconfident"
        },
        {
            "label": "自我认知准确型",
            "personality": {
                "openness": 0.70,
                "conscientiousness": 0.75,  # 高尽责性
                "extraversion": 0.60,
                "agreeableness": 0.65,
                "neuroticism": 0.40  # 适中神经质
            },
            "tendency": "accurate"
        },
        {
            "label": "过度谦虚型 (低估能力)",
            "personality": {
                "openness": 0.60,
                "conscientiousness": 0.80,  # 高尽责性
                "extraversion": 0.45,
                "agreeableness": 0.75,
                "neuroticism": 0.70  # 高神经质
            },
            "tendency": "underconfident"
        }
    ]
    
    for case in test_cases:
        print(f"\n{'-' * 80}")
        print(f"📊 {case['label']}")
        print(f"{'-' * 80}")
        print()
        
        p = case['personality']
        print("大五人格特质:")
        print(f"  开放性 (O): {p['openness']:.2f}")
        print(f"  尽责性 (C): {p['conscientiousness']:.2f}")
        print(f"  外向性 (E): {p['extraversion']:.2f}")
        print(f"  宜人性 (A): {p['agreeableness']:.2f}")
        print(f"  神经质 (N): {p['neuroticism']:.2f}")
        print()
        
        # 计算倾向分数
        overconfidence = (1 - p['conscientiousness']) * (1 - p['neuroticism'])
        underconfidence = p['conscientiousness'] * p['neuroticism']
        
        print(f"倾向计算:")
        print(f"  过度自信倾向 = (1-C) × (1-N) = {overconfidence:.3f}")
        print(f"  过度谦虚倾向 = C × N = {underconfidence:.3f}")
        print()
        
        # 解释预期行为
        if case['tendency'] == 'overconfident':
            print("⚠️  预期行为: 容易不懂装懂")
            print("   - 对不熟悉的领域也表现得很自信")
            print("   - 可能给出错误或片面的答案")
            print("   - 不太会承认自己不确定")
        elif case['tendency'] == 'underconfident':
            print("💭 预期行为: 容易过度谦虚")
            print("   - 即使擅长的领域也显得不确定")
            print("   - 频繁使用'我觉得'、'可能'等词汇")
            print("   - 过度强调还需要学习")
        else:
            print("✅ 预期行为: 准确评估能力")
            print("   - 擅长的领域展示信心")
            print("   - 不熟悉的领域诚实承认")


def demonstrate_knowledge_blind_spots():
    """展示知识盲区配置的效果"""
    print("\n\n" + "=" * 80)
    print("🎯 知识盲区配置示例")
    print("=" * 80)
    print()
    
    # 读取过度自信候选人配置
    print("📝 示例1: 过度自信候选人（不懂装懂）")
    print("-" * 80)
    
    overconfident_file = project_root / "config" / "candidate_templates" / "overconfident_candidate.json"
    if overconfident_file.exists():
        with open(overconfident_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        p = config['profile']['personality']
        print(f"候选人: {config['profile']['name']}")
        print(f"大五人格: C={p['conscientiousness']:.2f}, N={p['neuroticism']:.2f}")
        print(f"倾向: 低尽责性+低神经质 -> 过度自信")
        print()
        print("过度自信领域:")
        
        for area in config['profile']['knowledge_blind_spots']['overconfident_areas']:
            print(f"\n  🔴 {area['skill']}")
            print(f"     实际能力: {area['actual_level']}/10")
            print(f"     自我感觉: {area['perceived_level']}/10")
            print(f"     差距: +{area['perceived_level'] - area['actual_level']}")
            print(f"     说明: {area['description']}")
    
    print("\n\n" + "=" * 80)
    print("📝 示例2: 过度谦虚候选人（低估能力）")
    print("-" * 80)
    
    underconfident_file = project_root / "config" / "candidate_templates" / "underconfident_candidate.json"
    if underconfident_file.exists():
        with open(underconfident_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        p = config['profile']['personality']
        print(f"候选人: {config['profile']['name']}")
        print(f"大五人格: C={p['conscientiousness']:.2f}, N={p['neuroticism']:.2f}")
        print(f"倾向: 高尽责性+高神经质 -> 过度谦虚")
        print()
        print("过度谦虚领域:")
        
        for area in config['profile']['knowledge_blind_spots']['underconfident_areas']:
            print(f"\n  🟢 {area['skill']}")
            print(f"     实际能力: {area['actual_level']}/10")
            print(f"     自我感觉: {area['perceived_level']}/10")
            print(f"     差距: {area['perceived_level'] - area['actual_level']}")
            print(f"     说明: {area['description']}")


def show_usage_guide():
    """显示使用指南"""
    print("\n\n" + "=" * 80)
    print("📖 使用指南（基于大五人格模型）")
    print("=" * 80)
    print()
    print("1️⃣  运行面试时选择不同的候选人模板:")
    print("   - ideal_candidate.json: 正常候选人（无明显盲区）")
    print("   - overconfident_candidate.json: 过度自信，容易不懂装懂")
    print("   - underconfident_candidate.json: 过度谦虚，低估能力")
    print()
    print("2️⃣  自定义知识盲区:")
    print("   在候选人配置文件中添加 knowledge_blind_spots 字段")
    print()
    print("3️⃣  调整大五人格特质以影响知识误判倾向:")
    print("   过度自信 (不懂装懂):")
    print("     - conscientiousness: 低 (< 0.4)")
    print("     - neuroticism: 低 (< 0.4)")
    print("   过度谦虚 (低估能力):")
    print("     - conscientiousness: 高 (> 0.7)")
    print("     - neuroticism: 高 (> 0.7)")
    print("   准确认知:")
    print("     - conscientiousness: 高 (> 0.7)")
    print("     - neuroticism: 适中 (0.3-0.6)")
    print()
    print("4️⃣  测试不同技能的盲区:")
    print("   在 overconfident_areas 或 underconfident_areas 中指定技能")
    print()
    print("=" * 80)


def main():
    """主测试函数"""
    print("\n")
    print("🧪" * 40)
    print("知识误判机制测试（基于大五人格模型）")
    print("🧪" * 40)
    print()
    
    # 测试1: 大五人格与知识误判倾向
    demonstrate_personality_patterns()
    
    # 测试2: 知识盲区配置
    demonstrate_knowledge_blind_spots()
    
    # 显示使用指南
    show_usage_guide()
    
    print("\n✅ 测试完成！")
    print()


if __name__ == "__main__":
    main()
