"""
测试知识误判功能
演示过度自信（不懂装懂）和过度谦虚（低估能力）的效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.personality_generator import PersonalityGenerator
import json


def demonstrate_self_awareness_levels():
    """展示不同自知之明水平的效果"""
    print("=" * 80)
    print("🧠 自知之明水平对比测试")
    print("=" * 80)
    print()
    
    generator = PersonalityGenerator(seed=42)
    
    test_cases = [
        ("低自知之明 (不懂装懂)", 25),
        ("中等自知之明 (准确认知)", 55),
        ("高自知之明 (过度谦虚)", 85)
    ]
    
    for label, awareness_level in test_cases:
        print(f"\n{'-' * 80}")
        print(f"📊 {label} - self_awareness = {awareness_level}/100")
        print(f"{'-' * 80}")
        print()
        
        # 生成一个基础性格配置
        config = generator.generate_random("normal")
        
        # 修改自知之明水平
        config.self_perception["self_awareness"] = awareness_level
        
        print("性格配置:")
        print(f"  自信度: {config.response['confidence']}/100")
        print(f"  自知之明: {config.self_perception['self_awareness']}/100")
        print()
        
        # 解释预期行为
        if awareness_level < 50:
            print("⚠️  预期行为: 容易不懂装懂")
            print("   - 对不熟悉的领域也表现得很自信")
            print("   - 可能给出错误或片面的答案")
            print("   - 不太会承认自己不确定")
        elif awareness_level > 70:
            print("💭 预期行为: 容易过度谦虚")
            print("   - 即使擅长的领域也显得不确定")
            print("   - 频繁使用'我觉得'、'可能'等词汇")
            print("   - 过度强调还需要学习")
        else:
            print("✅预期行为: 准确评估能力")
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
        
        print(f"候选人: {config['profile']['name']}")
        print(f"自知之明: {config['profile']['personality']['self_perception']['self_awareness']}/100")
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
        
        print(f"候选人: {config['profile']['name']}")
        print(f"自知之明: {config['profile']['personality']['self_perception']['self_awareness']}/100")
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
    print("📖 使用指南")
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
    print("3️⃣  调整自知之明水平:")
    print("   修改 personality.self_perception.self_awareness 值")
    print("   - < 50: 容易不懂装懂")
    print("   - 50-70: 准确认知")
    print("   - > 70: 容易过度谦虚")
    print()
    print("4️⃣  测试不同技能的盲区:")
    print("   在 overconfident_areas 或 underconfident_areas 中指定技能")
    print()
    print("=" * 80)


def main():
    """主测试函数"""
    print("\n")
    print("🧪" * 40)
    print("知识误判机制测试")
    print("🧪" * 40)
    print()
    
    # 测试1: 自知之明水平对比
    demonstrate_self_awareness_levels()
    
    # 测试2: 知识盲区配置
    demonstrate_knowledge_blind_spots()
    
    # 显示使用指南
    show_usage_guide()
    
    print("\n✅ 测试完成！")
    print()


if __name__ == "__main__":
    main()
