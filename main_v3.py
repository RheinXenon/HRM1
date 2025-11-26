"""
智能面试系统 v3.0 - 主入口文件（统一架构版）

特性：
- 双Agent架构（面试官 + 候选人）
- 跨行业领域支持（tech/marketing/healthcare）
- 知识盲区检测（过度自信/过度谦虚）
- 智能追问系统（Few-Shot Negative Examples）
- 多维度评分（0-100标准化）
- 随机性格生成（4种策略 + 6种原型）

v3.0 改进：
- 所有模式统一支持领域选择
- 所有模式统一支持候选人类型选择（模板/随机生成）
- 更灵活的命令行参数组合
"""

import sys
import json
from pathlib import Path
from loguru import logger
from typing import Dict, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import load_candidate_template, load_job_config, load_company_config
from core import InterviewEngine
from core.personality_generator import PersonalityGenerator, create_random_candidate_config
from core.random_generator import RandomCandidateGenerator
from domains import list_available_domains, get_domain_info
from dataclasses import asdict


def select_mode() -> str:
    """交互式选择面试模式"""
    print("\n请选择面试模式:")
    print("1. Demo模式 - 快速演示（3个问题）")
    print("2. Full模式 - 完整面试（完整流程）")
    
    choice = input("\n请选择 (1-2, 默认1-Demo): ").strip() or "1"
    return "demo" if choice == "1" else "full"


def select_domain() -> str:
    """交互式选择领域"""
    domains = list_available_domains()
    print("\n可选的面试领域:")
    domain_map = {}
    for i, domain_id in enumerate(sorted(domains), 1):
        info = get_domain_info(domain_id)
        domain_name = info.get('domain_name', domain_id) if info else domain_id
        print(f"{i}. {domain_id} - {domain_name}")
        domain_map[str(i)] = domain_id
    
    choice = input(f"\n请选择领域 (1-{len(domains)}, 默认1): ").strip() or "1"
    return domain_map.get(choice, "tech")


def select_candidate_type() -> str:
    """交互式选择候选人类型"""
    print("\n候选人来源:")
    print("1. 使用预定义模板（理想、初级、过度自信等）")
    print("2. 随机生成候选人（性格/技能随机）")
    
    choice = input("\n请选择 (1-2, 默认1): ").strip() or "1"
    return "template" if choice == "1" else "random"


def select_template() -> str:
    """交互式选择候选人模板"""
    print("\n可选的候选人模板:")
    print("1. ideal_candidate - 理想候选人")
    print("2. junior_candidate - 初级候选人")
    print("3. nervous_candidate - 紧张型候选人")
    print("4. overconfident_candidate - 过度自信（不懂装懂）")
    print("5. underconfident_candidate - 过度谦虚（低估能力）")
    print("6. test_react_blind_spot - React知识盲区测试（推荐：测试追问机制）")
    
    template_map = {
        "1": "ideal_candidate",
        "2": "junior_candidate",
        "3": "nervous_candidate",
        "4": "overconfident_candidate",
        "5": "underconfident_candidate",
        "6": "test_react_blind_spot"
    }
    
    choice = input("\n请选择候选人 (1-6, 默认1): ").strip() or "1"
    return template_map.get(choice, "ideal_candidate")


def select_personality_strategy() -> tuple:
    """交互式选择性格生成策略"""
    print("\n可选的性格生成策略:")
    print("1. normal - 正态分布（推荐，更真实）")
    print("2. balanced - 平衡型（中等值）")
    print("3. extreme - 极端型（有趣的边界情况）")
    print("4. uniform - 完全随机")
    print()
    print("可选的性格原型（大五人格 O=开放性 C=尽责性 E=外向性 A=宜人性 N=神经质）:")
    print("5. confident - 自信型      [O:0.65 C:0.70 E:0.80 A:0.60 N:0.20]")
    print("6. anxious - 焦虑型        [O:0.50 C:0.65 E:0.30 A:0.55 N:0.75]")
    print("7. creative - 创造型       [O:0.85 C:0.55 E:0.65 A:0.60 N:0.45]")
    print("8. reliable - 可靠型       [O:0.55 C:0.85 E:0.50 A:0.70 N:0.30]")
    print("9. friendly - 友善型       [O:0.60 C:0.60 E:0.80 A:0.85 N:0.35]")
    print("10. analytical - 分析型    [O:0.75 C:0.80 E:0.45 A:0.50 N:0.40]")
    
    choice = input("\n请选择 (1-10, 默认1-normal): ").strip() or "1"
    
    strategy_map = {
        "1": ("normal", None),
        "2": ("balanced", None),
        "3": ("extreme", None),
        "4": ("uniform", None),
        "5": ("archetype", "confident"),
        "6": ("archetype", "anxious"),
        "7": ("archetype", "creative"),
        "8": ("archetype", "reliable"),
        "9": ("archetype", "friendly"),
        "10": ("archetype", "analytical")
    }
    
    return strategy_map.get(choice, ("normal", None))


def generate_candidate(candidate_type: str, domain_id: str, **kwargs) -> Dict:
    """
    统一的候选人生成函数
    
    Args:
        candidate_type: "template" 或 "random"
        domain_id: 领域ID
        **kwargs: 额外参数（template_name, strategy, archetype等）
    
    Returns:
        候选人配置字典
    """
    if candidate_type == "template":
        template_name = kwargs.get('template_name', 'ideal_candidate')
        logger.info(f"📋 加载候选人模板: {template_name}")
        return load_candidate_template(template_name)
    
    elif candidate_type == "random":
        strategy = kwargs.get('strategy', 'normal')
        archetype = kwargs.get('archetype', None)
        level = kwargs.get('level', 'mid')
        
        logger.info(f"🎲 生成随机候选人 [领域: {domain_id}, 策略: {strategy}]")
        
        # 生成性格
        generator = PersonalityGenerator()
        if archetype:
            personality_config = generator.generate_from_archetype(archetype)
        else:
            personality_config = generator.generate_random(strategy=strategy)
        
        # 转换PersonalityConfig为字典
        personality = asdict(personality_config)
        
        # 生成完整候选人（使用领域特定的技能）
        skill_generator = RandomCandidateGenerator(domain_id=domain_id)
        candidate_config = skill_generator.generate_complete_candidate(
            level=level,
            personality=personality
        )
        
        return candidate_config
    
    else:
        raise ValueError(f"未知的候选人类型: {candidate_type}")


def run_interview(
    mode: str = "demo",
    domain_id: str = None,
    candidate_type: str = None,
    **candidate_kwargs
) -> None:
    """
    统一的面试执行函数
    
    Args:
        mode: "demo" 或 "full"
        domain_id: 领域ID，None则交互选择
        candidate_type: "template" 或 "random"，None则交互选择
        **candidate_kwargs: 候选人生成参数
    """
    mode_name = "Demo模式" if mode == "demo" else "完整模式"
    print("\n" + "=" * 70)
    print(f"智能面试系统 v3.0 - {mode_name}")
    print("=" * 70)
    
    try:
        # 1. 确定领域
        if domain_id is None:
            domain_id = select_domain()
        
        domain_info = get_domain_info(domain_id)
        if domain_info:
            print(f"\n📋 选择的领域: {domain_info.get('domain_name', domain_id)}")
            print(f"   描述: {domain_info.get('description', '')}")
        
        # 2. 确定候选人类型和生成
        if candidate_type is None:
            candidate_type = select_candidate_type()
        
        if candidate_type == "template":
            if 'template_name' not in candidate_kwargs:
                candidate_kwargs['template_name'] = select_template()
        elif candidate_type == "random":
            if 'strategy' not in candidate_kwargs and 'archetype' not in candidate_kwargs:
                strategy, archetype = select_personality_strategy()
                candidate_kwargs['strategy'] = strategy
                if archetype:
                    candidate_kwargs['archetype'] = archetype
        
        # 生成候选人
        candidate_config = generate_candidate(candidate_type, domain_id, **candidate_kwargs)
        
        print(f"\n✅ 候选人: {candidate_config['profile']['name']}")
        print(f"   领域: {domain_id}")
        print(f"   技能数量: {len(candidate_config['profile']['skills'])}")
        
        # 显示前3个技能
        skills_preview = list(candidate_config['profile']['skills'].items())[:3]
        for skill, level in skills_preview:
            print(f"   - {skill}: {level}/10")
        
        # 显示性格特征（如果有）
        if 'personality' in candidate_config['profile']:
            personality = candidate_config['profile']['personality']
            print(f"   人格: O={personality.get('openness', 0.5):.2f}, "
                  f"C={personality.get('conscientiousness', 0.5):.2f}, "
                  f"E={personality.get('extraversion', 0.5):.2f}, "
                  f"A={personality.get('agreeableness', 0.5):.2f}, "
                  f"N={personality.get('neuroticism', 0.5):.2f}")
        print()
        
        # 3. 创建面试引擎
        logger.info(f"🤖 初始化{domain_id}领域面试引擎...")
        engine = InterviewEngine()
        
        # 4. 执行面试（使用动态生成的配置，无需指定配置文件）
        logger.info(f"🚀 开始{mode_name}面试流程...\n")
        
        result = engine.run_interview(
            candidate_config=candidate_config,
            mode=mode,
            domain_id=domain_id
            # 不传job_file和company_file，会自动根据domain_id动态生成
        )
        
        # 5. 显示评估结果
        print("\n" + "=" * 70)
        print(f"{domain_id.upper()}领域面试评估报告")
        print("=" * 70)
        print(f"\n🎯 推荐度评分: {result.recommendation_score}/100")
        
        evaluation = result.evaluation
        
        # 招聘建议
        if "recommendation" in evaluation:
            print(f"📝 招聘建议: {evaluation['recommendation']}")
        
        # 维度评分总结
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
        
        # 技能评分
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
            print(f"\n🔍 智能追问统计:")
            print(f"   追问次数: {followup_count}")
            print(f"   (使用{domain_id}领域专属的信号词汇检测)")
            
            # 显示追问示例
            followups = [qa for qa in result.conversation_log if qa.get('is_followup', False)]
            if followups:
                print(f"\n   追问示例:")
                for i, fq in enumerate(followups[:2], 1):
                    print(f"   [{i}] {fq.get('question', '')[:60]}...")
        
        print("\n" + "=" * 70)
        print(f"✅ {mode_name}完成! 领域: {domain_id.upper()}")
        print(f"📁 面试记录已保存: data/interviews/")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ 面试执行失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数 - 完全交互式"""
    
    # 显示欢迎信息
    print("\n" + "=" * 70)
    print("智能面试系统 v3.0")
    print("跨行业领域 | 知识盲区检测 | 智能追问")
    print("=" * 70)
    
    # 1. 选择面试模式
    mode = select_mode()
    
    # 运行面试（所有其他选项都在run_interview中交互选择）
    run_interview(mode=mode)


if __name__ == "__main__":
    main()
