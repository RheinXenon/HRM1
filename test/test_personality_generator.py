"""
测试大五人格生成器
展示不同策略和原型的人格生成效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.personality_generator import PersonalityGenerator, create_random_candidate_config, PersonalityConfig
import json


def test_strategies():
    """测试不同生成策略"""
    print("=" * 70)
    print("🎲 测试大五人格生成策略")
    print("=" * 70)
    
    generator = PersonalityGenerator(seed=42)  # 使用固定种子便于对比
    
    strategies = ["balanced", "extreme", "normal", "uniform"]
    
    for strategy in strategies:
        print(f"\n{'=' * 70}")
        print(f"策略: {strategy.upper()}")
        print("=" * 70)
        
        config = generator.generate_random(strategy)
        
        print(f"\n大五人格特质:")
        print(f"  开放性 (Openness):           {config.openness:.3f}")
        print(f"  尽责性 (Conscientiousness):  {config.conscientiousness:.3f}")
        print(f"  外向性 (Extraversion):        {config.extraversion:.3f}")
        print(f"  宜人性 (Agreeableness):       {config.agreeableness:.3f}")
        print(f"  神经质 (Neuroticism):         {config.neuroticism:.3f}")


def test_archetypes():
    """测试性格原型"""
    print("\n\n" + "=" * 70)
    print("🎭 测试性格原型")
    print("=" * 70)
    
    generator = PersonalityGenerator(seed=123)
    
    archetypes = [
        ("confident", "自信型"),
        ("anxious", "焦虑型"),
        ("creative", "创造型"),
        ("reliable", "可靠型"),
        ("friendly", "友善型"),
        ("analytical", "分析型")
    ]
    
    for archetype, desc in archetypes:
        print(f"\n{'=' * 70}")
        print(f"原型: {archetype.upper()} ({desc})")
        print("=" * 70)
        
        config = generator.generate_archetype(archetype)
        
        print(f"\n大五人格特质:")
        print(f"  开放性 (O): {config.openness:.3f}")
        print(f"  尽责性 (C): {config.conscientiousness:.3f}")
        print(f"  外向性 (E): {config.extraversion:.3f}")
        print(f"  宜人性 (A): {config.agreeableness:.3f}")
        print(f"  神经质 (N): {config.neuroticism:.3f}")


def test_random_candidate():
    """测试随机候选人生成"""
    print("\n\n" + "=" * 70)
    print("👤 测试完整候选人配置生成")
    print("=" * 70)
    
    print("\n生成3个随机候选人...\n")
    
    for i in range(3):
        print(f"\n--- 候选人 {i+1} ---")
        
        candidate = create_random_candidate_config(
            base_template="ideal_candidate",
            personality_strategy="normal"
        )
        
        print(f"姓名: {candidate['profile']['name']}")
        print(f"技能水平: Python={candidate['profile']['skills']['python']}/10, "
              f"System Design={candidate['profile']['skills']['system_design']}/10")
        
        personality = candidate['profile']['personality']
        print(f"人格: O={personality['openness']:.2f}, "
              f"C={personality['conscientiousness']:.2f}, "
              f"E={personality['extraversion']:.2f}, "
              f"A={personality['agreeableness']:.2f}, "
              f"N={personality['neuroticism']:.2f}")


def test_visual_comparison():
    """视觉化对比不同策略"""
    print("\n\n" + "=" * 70)
    print("📊 策略对比可视化")
    print("=" * 70)
    
    generator = PersonalityGenerator(seed=999)
    
    # 生成多个样本
    strategies = ["balanced", "extreme", "normal", "uniform"]
    samples = {s: [generator.generate_random(s) for _ in range(5)] for s in strategies}
    
    # 计算平均值
    print("\n各策略的平均值对比:")
    print("-" * 70)
    print(f"{'策略':<12} {'开放性':>8} {'尽责性':>8} {'外向性':>8} {'宜人性':>8} {'神经质':>8}")
    print("-" * 70)
    
    for strategy, configs in samples.items():
        avg_o = sum(c.openness for c in configs) / len(configs)
        avg_c = sum(c.conscientiousness for c in configs) / len(configs)
        avg_e = sum(c.extraversion for c in configs) / len(configs)
        avg_a = sum(c.agreeableness for c in configs) / len(configs)
        avg_n = sum(c.neuroticism for c in configs) / len(configs)
        
        print(f"{strategy:<12} {avg_o:>7.3f}  {avg_c:>7.3f}  {avg_e:>7.3f}  {avg_a:>7.3f}  {avg_n:>7.3f}")
    
    print("-" * 70)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "大五人格生成器测试工具" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # 运行所有测试
    test_strategies()
    test_archetypes()
    test_random_candidate()
    test_visual_comparison()
    
    print("\n\n" + "=" * 70)
    print("✅ 所有测试完成！")
    print("=" * 70)
    print("\n提示: 运行 'python main.py --mode random' 来使用随机性格进行面试")
    print()
