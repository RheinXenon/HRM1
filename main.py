"""
主入口文件 - 自动面试系统
"""

import sys
import json
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import load_candidate_template, load_job_config, load_company_config
from core import InterviewEngine
from core.personality_generator import PersonalityGenerator, create_random_candidate_config


def run_demo_interview():
    """运行Demo模式面试"""
    print("\n" + "=" * 60)
    print("🎯 自动面试系统 - Phase 1 MVP Demo")
    print("=" * 60)
    print()
    
    try:
        # 1. 加载候选人配置
        logger.info("📋 加载候选人配置...")
        candidate_config = load_candidate_template("ideal_candidate")
        
        print(f"✅ 候选人: {candidate_config['profile']['name']}")
        print(f"   技能等级: Python {candidate_config['profile']['skills']['python']}/10, "
              f"System Design {candidate_config['profile']['skills']['system_design']}/10")
        print(f"   工作经验: {candidate_config['profile']['experience']['years']}年")
        print()
        
        # 2. 创建面试引擎
        logger.info("🤖 初始化面试引擎...")
        engine = InterviewEngine()
        
        # 3. 执行面试
        logger.info("🚀 开始自动面试流程...\n")
        result = engine.run_interview(
            job_file="senior_backend",
            company_file="tech_startup",
            candidate_config=candidate_config,
            mode="demo"  # Demo模式：只问3个问题
        )
        
        # 4. 显示评估结果
        print("\n" + "=" * 60)
        print("📊 面试评估报告 (Phase 1: 标准化评分体系)")
        print("=" * 60)

        evaluation = result.evaluation

        # 推荐度 (标准化分数 0-100)
        print(f"\n🎯 推荐度评分: {result.recommendation_score}/100")

        # 招聘建议
        if "recommendation" in evaluation:
            print(f"📝 招聘建议: {evaluation['recommendation']}")

        # 维度评分总结 (Phase 1新增)
        if "dimension_scores_summary" in evaluation:
            print("\n📋 多维度评分 (1-4分):")
            dimension_names = {
                "technical_depth": "技术深度",
                "practical_experience": "实践经验",
                "answer_specificity": "回答具体性",
                "logical_clarity": "逻辑清晰度",
                "honesty": "诚实度",
                "communication": "沟通能力"
            }
            for dim_key, score in evaluation['dimension_scores_summary'].items():
                dim_name = dimension_names.get(dim_key, dim_key)
                print(f"   - {dim_name}: {score}/4")

        # 技能评分 (标准化分数 0-100)
        if "skill_scores" in evaluation:
            print("\n💪 技能评分 (标准化分数):")
            for skill, score in list(evaluation['skill_scores'].items())[:8]:
                print(f"   - {skill}: {score}/100")

        # 优势
        if "strengths" in evaluation:
            print("\n✨ 优势:")
            for strength in evaluation['strengths'][:3]:
                print(f"   - {strength}")

        # 改进建议
        if "improvements" in evaluation:
            print("\n📈 待改进:")
            for improvement in evaluation['improvements'][:3]:
                print(f"   - {improvement}")

        # 总结
        if result.summary:
            print(f"\n📄 总结:\n{result.summary}")

        print("\n" + "=" * 60)
        print("✅ Demo 完成! (Phase 1: 多维度评分 + 标准化)")
        print(f"📁 面试记录已保存: data/interviews/")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 面试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return


def run_full_interview():
    """运行完整模式面试"""
    print("\n" + "=" * 60)
    print("🎯 自动面试系统 - 完整模式")
    print("=" * 60)
    
    try:
        # 让用户选择候选人模板
        print("\n可选的候选人模板:")
        print("1. ideal_candidate - 理想候选人")
        print("2. junior_candidate - 初级候选人")
        print("3. nervous_candidate - 紧张型候选人")
        print("4. overconfident_candidate - 过度自信（不懂装懂）")
        print("5. underconfident_candidate - 过度谦虚（低估能力）")
        
        choice = input("\n请选择候选人 (1-5, 默认1): ").strip() or "1"
        
        template_map = {
            "1": "ideal_candidate",
            "2": "junior_candidate",
            "3": "nervous_candidate",
            "4": "overconfident_candidate",
            "5": "underconfident_candidate"
        }
        
        template_name = template_map.get(choice, "ideal_candidate")
        candidate_config = load_candidate_template(template_name)
        
        logger.info(f"已选择: {candidate_config.get('template_name', template_name)}")
        
        # 创建面试引擎
        engine = InterviewEngine()
        
        # 执行完整面试
        result = engine.run_interview(
            job_file="senior_backend",
            company_file="tech_startup",
            candidate_config=candidate_config,
            mode="full"  # 完整模式：所有问题
        )
        
        print(f"\n✅ 面试完成! 推荐度: {result.recommendation_score}/100")
        
    except Exception as e:
        logger.error(f"❌ 面试执行失败: {e}")
        import traceback
        traceback.print_exc()


def run_random_personality_interview():
    """运行随机性格面试"""
    print("\n" + "=" * 60)
    print("🎲 自动面试系统 - 随机性格模式")
    print("=" * 60)
    print()
    
    try:
        # 选择性格生成策略
        print("可选的性格生成策略:")
        print("1. normal - 正态分布（推荐，更真实）")
        print("2. balanced - 平衡型（中等值）")
        print("3. extreme - 极端型（有趣的边界情况）")
        print("4. uniform - 完全随机")
        print()
        print("可选的性格原型:")
        print("5. confident - 自信型")
        print("6. nervous - 紧张型")
        print("7. technical - 技术型")
        print("8. storyteller - 叙事型")
        print("9. enthusiastic - 热情型")
        print("10. reserved - 保守型")
        
        choice = input("\n请选择 (1-10, 默认1): ").strip() or "1"
        
        # 创建性格生成器
        generator = PersonalityGenerator()
        
        # 根据选择生成性格
        if choice in ["1", "2", "3", "4"]:
            strategy_map = {
                "1": "normal",
                "2": "balanced",
                "3": "extreme",
                "4": "uniform"
            }
            strategy = strategy_map[choice]
            print(f"\n🎲 使用策略: {strategy}")
            
            # 生成随机候选人配置
            candidate_config = create_random_candidate_config(
                base_template="ideal_candidate",
                personality_strategy=strategy
            )
        else:
            archetype_map = {
                "5": "confident",
                "6": "nervous",
                "7": "technical",
                "8": "storyteller",
                "9": "enthusiastic",
                "10": "reserved"
            }
            archetype = archetype_map.get(choice, "confident")
            print(f"\n🎭 使用原型: {archetype}")
            
            # 加载基础模板
            candidate_config = load_candidate_template("ideal_candidate")
            # 生成原型性格
            personality = generator.generate_archetype(archetype)
            candidate_config['profile']['personality'] = personality.to_dict()
        
        # 显示生成的性格
        print("\n✨ 生成的性格特质:")
        personality = candidate_config['profile']['personality']
        print(f"  沟通风格: verbose={personality['communication']['verbose']}, "
              f"technical={personality['communication']['technical']}")
        print(f"  回答特征: confidence={personality['response']['confidence']}, "
              f"detail={personality['response']['detail_orientation']}, "
              f"storytelling={personality['response']['storytelling']}")
        print(f"  情绪表现: nervousness={personality['emotion']['nervousness']}, "
              f"enthusiasm={personality['emotion']['enthusiasm']}")
        print()
        
        # 询问是否保存
        save = input("是否保存此性格配置？(y/N): ").strip().lower()
        if save == 'y':
            filename = input("输入文件名（不含扩展名）: ").strip()
            if filename:
                output_dir = Path("config/candidate_templates/generated")
                output_dir.mkdir(parents=True, exist_ok=True)
                filepath = output_dir / f"{filename}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(candidate_config, f, indent=2, ensure_ascii=False)
                print(f"✅ 配置已保存至: {filepath}")
        
        # 创建面试引擎
        logger.info("🤖 初始化面试引擎...")
        engine = InterviewEngine()
        
        # 执行面试
        logger.info("🚀 开始自动面试流程...\n")
        result = engine.run_interview(
            job_file="senior_backend",
            company_file="tech_startup",
            candidate_config=candidate_config,
            mode="demo"
        )
        
        # 显示评估结果
        print("\n" + "=" * 60)
        print("📊 面试评估报告 (Phase 1: 标准化评分体系)")
        print("=" * 60)

        evaluation = result.evaluation

        print(f"\n🎯 推荐度评分: {result.recommendation_score}/100")

        if "recommendation" in evaluation:
            print(f"📝 招聘建议: {evaluation['recommendation']}")

        # 维度评分总结 (Phase 1新增)
        if "dimension_scores_summary" in evaluation:
            print("\n📋 多维度评分 (1-4分):")
            dimension_names = {
                "technical_depth": "技术深度",
                "practical_experience": "实践经验",
                "answer_specificity": "回答具体性",
                "logical_clarity": "逻辑清晰度",
                "honesty": "诚实度",
                "communication": "沟通能力"
            }
            for dim_key, score in evaluation['dimension_scores_summary'].items():
                dim_name = dimension_names.get(dim_key, dim_key)
                print(f"   - {dim_name}: {score}/4")

        if "skill_scores" in evaluation:
            print("\n💪 技能评分 (标准化分数):")
            for skill, score in list(evaluation['skill_scores'].items())[:8]:
                print(f"   - {skill}: {score}/100")

        if "strengths" in evaluation:
            print("\n✨ 优势:")
            for strength in evaluation['strengths'][:3]:
                print(f"   - {strength}")

        if "improvements" in evaluation:
            print("\n📈 待改进:")
            for improvement in evaluation['improvements'][:3]:
                print(f"   - {improvement}")

        if result.summary:
            print(f"\n📄 总结:\n{result.summary}")

        print("\n" + "=" * 60)
        print("✅ 随机性格面试完成! (Phase 1: 多维度评分 + 标准化)")
        print(f"📁 面试记录已保存: data/interviews/")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 面试执行失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动面试系统 - Phase 1 MVP")
    parser.add_argument(
        "--mode",
        choices=["demo", "full", "random"],
        default="demo",
        help="面试模式: demo(快速演示) / full(完整面试) / random(随机性格)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "demo":
        run_demo_interview()
    elif args.mode == "random":
        run_random_personality_interview()
    else:
        run_full_interview()


if __name__ == "__main__":
    main()
