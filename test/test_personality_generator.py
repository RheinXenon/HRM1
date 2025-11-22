"""
测试性格生成器
展示不同策略和原型的性格生成效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.personality_generator import PersonalityGenerator, create_random_candidate_config
import json


def test_strategies():
    """测试不同生成策略"""
    print("=" * 70)
    print("🎲 测试性格生成策略")
    print("=" * 70)
    
    generator = PersonalityGenerator(seed=42)  # 使用固定种子便于对比
    
    strategies = ["balanced", "extreme", "normal", "uniform"]
    
    for strategy in strategies:
        print(f"\n{'=' * 70}")
        print(f"策略: {strategy.upper()}")
        print("=" * 70)
        
        config = generator.generate_random(strategy)
        
        print(f"\n沟通风格:")
        print(f"  啰嗦程度: {config.communication['verbose']:2d}/100")
        print(f"  技术用词: {config.communication['technical']:2d}/100")
        
        print(f"\n回答特征:")
        print(f"  自信度:   {config.response['confidence']:2d}/100")
        print(f"  细节程度: {config.response['detail_orientation']:2d}/100")
        print(f"  叙事能力: {config.response['storytelling']:2d}/100")
        
        print(f"\n情绪表现:")
        print(f"  紧张度:   {config.emotion['nervousness']:2d}/100")
        print(f"  热情度:   {config.emotion['enthusiasm']:2d}/100")


def test_archetypes():
    """测试性格原型"""
    print("\n\n" + "=" * 70)
    print("🎭 测试性格原型")
    print("=" * 70)
    
    generator = PersonalityGenerator(seed=123)
    
    archetypes = [
        ("confident", "自信型"),
        ("nervous", "紧张型"),
        ("technical", "技术型"),
        ("storyteller", "叙事型"),
        ("enthusiastic", "热情型"),
        ("reserved", "保守型")
    ]
    
    for archetype, desc in archetypes:
        print(f"\n{'=' * 70}")
        print(f"原型: {archetype.upper()} ({desc})")
        print("=" * 70)
        
        config = generator.generate_archetype(archetype)
        
        print(f"\n沟通: verbose={config.communication['verbose']:2d}, "
              f"technical={config.communication['technical']:2d}")
        print(f"回答: confidence={config.response['confidence']:2d}, "
              f"detail={config.response['detail_orientation']:2d}, "
              f"storytelling={config.response['storytelling']:2d}")
        print(f"情绪: nervousness={config.emotion['nervousness']:2d}, "
              f"enthusiasm={config.emotion['enthusiasm']:2d}")


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
        print(f"性格: confidence={personality['response']['confidence']}, "
              f"nervousness={personality['emotion']['nervousness']}, "
              f"enthusiasm={personality['emotion']['enthusiasm']}")


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
    print(f"{'策略':<12} {'自信度':>8} {'紧张度':>8} {'热情度':>8} {'技术性':>8}")
    print("-" * 70)
    
    for strategy, configs in samples.items():
        avg_conf = sum(c.response['confidence'] for c in configs) / len(configs)
        avg_nerv = sum(c.emotion['nervousness'] for c in configs) / len(configs)
        avg_enth = sum(c.emotion['enthusiasm'] for c in configs) / len(configs)
        avg_tech = sum(c.communication['technical'] for c in configs) / len(configs)
        
        print(f"{strategy:<12} {avg_conf:>7.1f}  {avg_nerv:>7.1f}  {avg_enth:>7.1f}  {avg_tech:>7.1f}")
    
    print("-" * 70)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "性格生成器测试工具" + " " * 28 + "║")
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
