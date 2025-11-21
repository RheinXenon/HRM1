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
        print("📊 面试评估报告")
        print("=" * 60)
        
        evaluation = result.evaluation
        
        # 推荐度
        print(f"\n🎯 推荐度评分: {result.recommendation_score}/100")
        
        # 招聘建议
        if "recommendation" in evaluation:
            print(f"📝 招聘建议: {evaluation['recommendation']}")
        
        # 技能评分
        if "skill_scores" in evaluation:
            print("\n💪 技能评分:")
            for skill, score in evaluation['skill_scores'].items():
                print(f"   - {skill}: {score}/10")
        
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
        print("✅ Demo 完成!")
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
        
        choice = input("\n请选择候选人 (1-3, 默认1): ").strip() or "1"
        
        template_map = {
            "1": "ideal_candidate",
            "2": "junior_candidate",
            "3": "nervous_candidate"
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


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动面试系统 - Phase 1 MVP")
    parser.add_argument(
        "--mode",
        choices=["demo", "full"],
        default="demo",
        help="面试模式: demo(快速演示) 或 full(完整面试)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "demo":
        run_demo_interview()
    else:
        run_full_interview()


if __name__ == "__main__":
    main()
