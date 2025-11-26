"""
Phase 1 评分标准化测试脚本
测试多维度评分和标准化功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.score_normalizer import ScoreNormalizer, EVALUATION_DIMENSIONS
from loguru import logger

def test_score_normalizer():
    """测试评分标准化器"""
    print("\n" + "=" * 60)
    print("🧪 测试 Phase 1: 评分标准化器")
    print("=" * 60)

    normalizer = ScoreNormalizer()

    # 测试用例
    test_cases = [
        {
            "name": "优秀候选人",
            "scores": {
                "technical_depth": 4,
                "practical_experience": 4,
                "answer_specificity": 3,
                "logical_clarity": 4,
                "honesty": 4,
                "communication": 3
            },
            "expected_range": (75, 100)
        },
        {
            "name": "普通候选人",
            "scores": {
                "technical_depth": 2,
                "practical_experience": 2,
                "answer_specificity": 2,
                "logical_clarity": 3,
                "honesty": 3,
                "communication": 2
            },
            "expected_range": (40, 60)
        },
        {
            "name": "不懂装懂候选人",
            "scores": {
                "technical_depth": 2,
                "practical_experience": 1,
                "answer_specificity": 1,
                "logical_clarity": 2,
                "honesty": 1,  # 关键：诚实度很低
                "communication": 3
            },
            "expected_range": (0, 40)
        }
    ]

    all_passed = True

    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['name']}")
        print(f"维度评分: {case['scores']}")

        # 计算标准化分数
        score = normalizer.normalize_dimension_scores(case['scores'])
        interpretation = normalizer.get_score_interpretation(score)

        print(f"标准化分数: {score:.1f}/100")
        print(f"评价等级: {interpretation['interpretation']}")
        print(f"招聘建议: {interpretation['recommendation']}")
        print(f"百分位: 第{interpretation['percentile']:.1f}百分位")

        # 验证分数范围
        expected_min, expected_max = case['expected_range']
        if expected_min <= score <= expected_max:
            print(f"✅ 通过: 分数在预期范围 [{expected_min}, {expected_max}]")
        else:
            print(f"❌ 失败: 分数 {score:.1f} 不在预期范围 [{expected_min}, {expected_max}]")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)

    return all_passed


def test_evaluation_dimensions():
    """测试评估维度定义"""
    print("\n" + "=" * 60)
    print("🧪 测试评估维度定义")
    print("=" * 60)

    print(f"\n共定义了 {len(EVALUATION_DIMENSIONS)} 个评估维度:")

    for dim_key, dim_info in EVALUATION_DIMENSIONS.items():
        print(f"\n{dim_info['name']} ({dim_key}):")
        for score, description in dim_info['anchors'].items():
            print(f"  {score}分: {description}")

    # 验证所有维度都有4个锚点
    all_valid = True
    for dim_key, dim_info in EVALUATION_DIMENSIONS.items():
        if len(dim_info['anchors']) != 4:
            print(f"❌ 错误: {dim_key} 的锚点数量不是4")
            all_valid = False

    if all_valid:
        print("\n✅ 所有维度定义正确")

    return all_valid


def test_weights():
    """测试权重配置"""
    print("\n" + "=" * 60)
    print("🧪 测试维度权重")
    print("=" * 60)

    normalizer = ScoreNormalizer()
    weights = normalizer.get_dimension_weights()

    print("\n当前权重配置:")
    for dim, weight in weights.items():
        print(f"  {dim}: {weight:.2%}")

    total_weight = sum(weights.values())
    print(f"\n权重总和: {total_weight:.4f}")

    if abs(total_weight - 1.0) < 0.001:
        print("✅ 权重总和正确 (= 1.0)")
        return True
    else:
        print(f"❌ 权重总和错误 (应为1.0)")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("🚀 Phase 1 功能测试套件")
    print("=" * 80)

    results = []

    # 测试1: 评估维度定义
    results.append(("评估维度定义", test_evaluation_dimensions()))

    # 测试2: 权重配置
    results.append(("维度权重", test_weights()))

    # 测试3: 评分标准化器
    results.append(("评分标准化器", test_score_normalizer()))

    # 总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 Phase 1 所有测试通过!")
        print("✅ 多维度评分系统已就绪")
        print("✅ 标准化评分体系正常工作")
    else:
        print("⚠️  部分测试失败，请检查")
    print("=" * 80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
