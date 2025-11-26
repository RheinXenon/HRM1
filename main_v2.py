"""
智能面试系统 v2.0 - 主入口文件

特性：
- 双Agent架构（面试官 + 候选人）
- 跨行业领域支持（tech/marketing/healthcare）
- 知识盲区检测（过度自信/过度谦虚）
- 智能追问系统（Few-Shot Negative Examples）
- 多维度评分（0-100标准化）
- 随机性格生成（4种策略 + 6种原型）
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
from domains import list_available_domains, get_domain_info


def run_demo_interview():
    """运行Demo模式面试（Tech领域）"""
    print("\n" + "=" * 80)
    print("🎯 智能面试系统 v2.0 - Demo模式")
    print("支持跨行业领域 | 知识盲区检测 | 智能追问机制")
    print("=" * 80)
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
        print("\n" + "=" * 80)
        print("📊 面试评估报告")
        print("=" * 80)

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

        # 显示追问统计
        followup_count = sum(1 for qa in result.conversation_log if qa.get('is_followup', False))
        if followup_count > 0:
            print(f"\n🔍 智能追问次数: {followup_count}")
            print("   (检测到浅层回答，自动深入追问验证能力)")
        
        print("\n" + "=" * 80)
        print("✅ Demo完成! 领域: Tech | 版本: v2.0")
        print(f"📁 面试记录已保存: data/interviews/")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ 面试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return


def run_full_interview():
    """运行完整模式面试（支持知识盲区测试）"""
    print("\n" + "=" * 80)
    print("🎯 智能面试系统 v2.0 - 完整模式")
    print("=" * 80)
    
    try:
        # 让用户选择候选人模板
        print("\n可选的候选人模板:")
        print("1. ideal_candidate - 理想候选人")
        print("2. junior_candidate - 初级候选人")
        print("3. nervous_candidate - 紧张型候选人")
        print("4. overconfident_candidate - 过度自信（不懂装懂）")
        print("5. underconfident_candidate - 过度谦虚（低估能力）")
        print("6. test_react_blind_spot - React知识盲区测试（推荐：测试追问机制）")
        
        choice = input("\n请选择候选人 (1-6, 默认1): ").strip() or "1"
        
        template_map = {
            "1": "ideal_candidate",
            "2": "junior_candidate",
            "3": "nervous_candidate",
            "4": "overconfident_candidate",
            "5": "underconfident_candidate",
            "6": "test_react_blind_spot"
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
        
        # 显示详细结果
        print("\n" + "=" * 80)
        print("📊 面试评估报告")
        print("=" * 80)
        print(f"\n🎯 推荐度评分: {result.recommendation_score}/100")
        
        # 显示追问统计
        followup_count = sum(1 for qa in result.conversation_log if qa.get('is_followup', False))
        if followup_count > 0:
            print(f"\n🔍 智能追问统计:")
            print(f"   追问次数: {followup_count}")
            print(f"   触发原因: 检测到浅层回答、高级术语堆砌、缺乏具体证据")
            
            # 显示追问示例
            followups = [qa for qa in result.conversation_log if qa.get('is_followup', False)]
            if followups:
                print(f"\n   追问示例:")
                for i, fq in enumerate(followups[:2], 1):
                    print(f"   [{i}] {fq.get('question', '')[:60]}...")
        
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

        print("\n" + "=" * 80)
        print("✅ 随机性格面试完成! 版本: v2.0")
        print(f"📁 面试记录已保存: data/interviews/")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ 面试执行失败: {e}")
        import traceback
        traceback.print_exc()


def run_cross_domain_demo():
    """运行跨领域演示（展示领域通用化能力）"""
    print("\n" + "=" * 80)
    print("🌍 智能面试系统 v2.0 - 跨领域演示")
    print("展示Tech/Marketing/Healthcare三大领域通用化能力")
    print("=" * 80)
    print()
    
    try:
        # 显示可用领域
        domains = list_available_domains()
        print(f"✅ 系统支持的领域: {', '.join(domains)}\n")
        
        # 选择领域
        print("请选择面试领域:")
        print("1. tech - 技术/互联网（Python、Java、架构等39个技能）")
        print("2. marketing - 营销/传媒（品牌、内容、数字营销等34个技能）")
        print("3. healthcare - 医疗/护理（临床、专科、管理等35个技能）")
        
        domain_choice = input("\n请选择 (1-3, 默认1): ").strip() or "1"
        domain_map = {"1": "tech", "2": "marketing", "3": "healthcare"}
        domain_id = domain_map.get(domain_choice, "tech")
        
        # 显示领域信息
        domain_info = get_domain_info(domain_id)
        if domain_info:
            print(f"\n📋 领域信息:")
            print(f"   名称: {domain_info.get('domain_name', domain_id)}")
            print(f"   描述: {domain_info.get('description', '')}")
            industries = domain_info.get('applicable_industries', [])
            print(f"   适用行业: {', '.join(industries[:5])}")
        
        # 根据领域选择配置
        config_map = {
            "tech": {
                "job": "senior_backend",
                "company": "tech_startup",
                "template": "ideal_candidate"
            },
            "marketing": {
                "job": "senior_backend",  # TODO: 需要创建marketing_manager.json
                "company": "tech_startup",  # TODO: 需要创建marketing_agency.json
                "template": "ideal_candidate"
            },
            "healthcare": {
                "job": "senior_backend",  # TODO: 需要创建nurse.json
                "company": "tech_startup",  # TODO: 需要创建hospital.json
                "template": "ideal_candidate"
            }
        }
        
        config = config_map[domain_id]
        
        # 为非tech领域生成随机候选人
        if domain_id != "tech":
            from core.random_generator import RandomCandidateGenerator
            print(f"\n🎲 使用{domain_id}领域生成随机候选人...")
            generator = RandomCandidateGenerator(domain_id=domain_id)
            candidate_config = generator.generate_complete_candidate(level="mid")
        else:
            candidate_config = load_candidate_template(config["template"])
        
        print(f"\n✅ 候选人: {candidate_config['profile']['name']}")
        print(f"   技能数量: {len(candidate_config['profile']['skills'])}")
        skills_preview = list(candidate_config['profile']['skills'].items())[:3]
        for skill, level in skills_preview:
            print(f"   - {skill}: {level}/10")
        print()
        
        # 创建面试引擎
        logger.info(f"🤖 初始化{domain_id}领域面试引擎...")
        engine = InterviewEngine()
        
        # 执行面试
        logger.info(f"🚀 开始{domain_id}领域面试流程...\n")
        result = engine.run_interview(
            job_file=config["job"],
            company_file=config["company"],
            candidate_config=candidate_config,
            mode="demo",
            domain_id=domain_id  # 关键参数：指定领域
        )
        
        # 显示评估结果
        print("\n" + "=" * 80)
        print(f"📊 {domain_id.upper()}领域面试评估报告")
        print("=" * 80)
        print(f"\n🎯 推荐度评分: {result.recommendation_score}/100")
        
        # 显示追问统计
        followup_count = sum(1 for qa in result.conversation_log if qa.get('is_followup', False))
        if followup_count > 0:
            print(f"\n🔍 智能追问次数: {followup_count}")
            print(f"   (使用{domain_id}领域专属的信号词汇检测)")
        
        print("\n" + "=" * 80)
        print(f"✅ {domain_id.upper()}领域面试完成! 版本: v2.0")
        print(f"📁 面试记录已保存: data/interviews/")
        print(f"\n💡 提示: 系统已成功使用{domain_id}领域的技能分类和评估标准")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ 面试执行失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="智能面试系统 v2.0 - 支持跨行业领域、知识盲区检测、智能追问",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --mode demo          # 快速演示（Tech领域）
  python main.py --mode full          # 完整面试（支持知识盲区测试）
  python main.py --mode random        # 随机性格生成
  python main.py --mode domain        # 跨领域演示（Tech/Marketing/Healthcare）

功能特性:
  - 双Agent架构（面试官 + 候选人自动对话）
  - 跨行业支持（tech/marketing/healthcare，可扩展）
  - 知识盲区检测（过度自信/过度谦虚）
  - 智能追问机制（Few-Shot Negative Examples）
  - 多维度评分（0-100标准化）
  - 随机性格生成（4种策略 + 6种原型）
        """
    )
    parser.add_argument(
        "--mode",
        choices=["demo", "full", "random", "domain"],
        default="demo",
        help="面试模式: demo(快速演示) / full(完整面试) / random(随机性格) / domain(跨领域演示)"
    )
    
    args = parser.parse_args()
    
    # 显示欢迎信息
    if args.mode != "demo":
        print("\n" + "🤖" * 40)
        print("   智能面试系统 v2.0")
        print("   跨行业领域 | 知识盲区检测 | 智能追问机制")
        print("🤖" * 40)
    
    # 路由到对应的模式
    if args.mode == "demo":
        run_demo_interview()
    elif args.mode == "random":
        run_random_personality_interview()
    elif args.mode == "domain":
        run_cross_domain_demo()
    else:
        run_full_interview()


if __name__ == "__main__":
    main()
