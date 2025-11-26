"""
医护场景追问功能测试
使用full模式，测试面试官是否能正常触发追问机制
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import random
from loguru import logger
from core.interview_engine import InterviewEngine
from core.llm_client import LLMClient
from domains import DomainLoader


def create_test_candidate(domain_id: str = "healthcare"):
    """
    动态创建测试候选人配置（基于领域配置，无硬编码）
    
    Args:
        domain_id: 领域ID
        
    Returns:
        候选人配置字典
    """
    # 加载领域配置
    domain_loader = DomainLoader(domain_id)
    domain_config = domain_loader.get_domain_config()
    skills_taxonomy = domain_loader.get_skills_taxonomy()
    
    # 从领域配置中获取数据源
    typical_roles = domain_config.get("typical_roles", ["专员"])
    typical_projects = domain_config.get("typical_projects", ["项目A", "项目B"])
    typical_achievements = domain_config.get("typical_achievements", ["完成任务"])
    
    # 获取所有技能
    all_skills = []
    skill_descriptions = skills_taxonomy.get("skill_descriptions", {})
    for category_data in skills_taxonomy.get("skill_categories", {}).values():
        all_skills.extend(category_data.get("skills", []))
    
    # 随机生成候选人姓名（通用中文姓名，非领域特定）
    surnames = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴"]
    given_names = ["明", "华", "丽", "芳", "伟", "静", "强", "敏", "军", "娟"]
    candidate_name = random.choice(surnames) + random.choice(given_names)
    
    # 随机选择工作年限和职级
    years = random.randint(2, 5)
    level = "mid" if years >= 3 else "junior"
    
    # 随机生成技能（从领域技能中选择）
    num_skills = min(len(all_skills), random.randint(6, 10))
    selected_skills = random.sample(all_skills, num_skills)
    
    skills = {}
    for skill in selected_skills:
        # 随机生成技能等级 (3-8)
        skills[skill] = random.randint(3, 8)
    
    # 随机选择2-3个项目
    num_projects = random.randint(2, 3)
    selected_projects = random.sample(typical_projects, min(num_projects, len(typical_projects)))
    
    # 项目角色（尝试从领域角色派生，否则使用通用角色）
    if typical_roles:
        # 使用领域典型角色
        roles_in_projects = typical_roles
    else:
        # 后备：通用角色（非领域特定）
        roles_in_projects = ["成员", "负责人", "协调员", "主管", "专员"]
    
    projects = []
    for project_name in selected_projects:
        achievement = random.choice(typical_achievements)
        projects.append({
            "name": project_name,
            "role": random.choice(roles_in_projects),
            "achievement": achievement
        })
    
    # 随机生成人格特征（容易过度自信的配置）
    personality = {
        "openness": round(random.uniform(0.55, 0.75), 2),
        "conscientiousness": round(random.uniform(0.35, 0.55), 2),  # 低尽责性
        "extraversion": round(random.uniform(0.60, 0.80), 2),
        "agreeableness": round(random.uniform(0.55, 0.75), 2),
        "neuroticism": round(random.uniform(0.20, 0.40), 2)  # 低神经质 -> 容易过度自信
    }
    
    # 动态生成知识盲区（从技能中随机选择1-3个作为盲区）
    num_blind_spots = random.randint(1, min(3, len(selected_skills)))
    blind_spot_skills = random.sample(selected_skills, num_blind_spots)
    
    overconfident_areas = []
    for skill in blind_spot_skills:
        actual_level = random.randint(3, 5)  # 实际能力较低
        perceived_level = random.randint(7, 9)  # 自我认知较高
        skill_desc = skill_descriptions.get(skill, skill)
        
        overconfident_areas.append({
            "skill": skill,
            "actual_level": actual_level,
            "perceived_level": perceived_level,
            "description": f"对{skill_desc}有基础了解，但实战经验有限，容易过度自信地谈论高级话题"
        })
    
    return {
        "profile": {
            "name": candidate_name,
            "skills": skills,
            "experience": {
                "years": years,
                "level": level,
                "projects": projects
            },
            "personality": personality,
            "knowledge_blind_spots": {
                "overconfident_areas": overconfident_areas,
                "underconfident_areas": []
            }
        }
    }


def analyze_followup_triggers(conversation_log):
    """
    分析对话记录中的追问触发情况
    
    Args:
        conversation_log: 对话日志
        
    Returns:
        Dict: 追问统计信息
    """
    total_questions = 0
    followup_count = 0
    followup_details = []
    
    for entry in conversation_log:
        if entry.get("role") == "interviewer":
            # 统计问题总数
            if entry.get("type") != "followup":
                total_questions += 1
            
            # 统计追问
            if entry.get("type") == "followup":
                followup_count += 1
                followup_details.append({
                    "question": entry.get("content", ""),
                    "reason": entry.get("reason", "未知原因")
                })
    
    return {
        "total_questions": total_questions,
        "followup_count": followup_count,
        "followup_rate": followup_count / total_questions if total_questions > 0 else 0,
        "followup_details": followup_details
    }


def test_followup_mechanism():
    """
    测试追问机制
    使用full模式和医护场景
    """
    print("\n" + "=" * 80)
    print("🏥 医护场景追问功能测试 (Full模式)")
    print("=" * 80)
    print()
    
    # 动态创建测试候选人（基于医护领域配置，无硬编码）
    candidate_config = create_test_candidate(domain_id="healthcare")
    candidate_name = candidate_config["profile"]["name"]
    
    print(f"📋 测试候选人: {candidate_name}")
    print(f"   工作年限: {candidate_config['profile']['experience']['years']}年")
    print(f"   职级: {candidate_config['profile']['experience']['level']}")
    print()
    
    # 显示知识盲区
    blind_spots = candidate_config["profile"]["knowledge_blind_spots"]["overconfident_areas"]
    if blind_spots:
        print("🎯 设置的知识盲区（容易触发追问）:")
        for spot in blind_spots:
            print(f"   • {spot['skill']}: 实际能力={spot['actual_level']}/10, 自我认知={spot['perceived_level']}/10")
        print()
    
    # 创建面试引擎
    print("-" * 80)
    print("🚀 启动面试引擎 (full模式, healthcare场景)")
    print("-" * 80)
    print()
    
    llm_client = LLMClient()
    engine = InterviewEngine(llm_client=llm_client)
    
    # 运行面试
    result = engine.run_interview(
        candidate_config=candidate_config,
        mode="full",  # 使用full模式
        domain_id="healthcare"  # 使用医护场景
    )
    
    # 分析追问触发情况
    print("\n" + "=" * 80)
    print("📊 追问触发分析")
    print("=" * 80)
    print()
    
    analysis = analyze_followup_triggers(result.conversation_log)
    
    print(f"问题统计:")
    print(f"   总问题数: {analysis['total_questions']}")
    print(f"   追问次数: {analysis['followup_count']}")
    print(f"   追问率: {analysis['followup_rate']:.1%}")
    print()
    
    if analysis['followup_details']:
        print(f"追问详情:")
        for i, detail in enumerate(analysis['followup_details'], 1):
            print(f"\n   追问 {i}:")
            print(f"   问题: {detail['question'][:100]}...")
            print(f"   原因: {detail['reason']}")
    else:
        print("⚠️  未触发任何追问")
    
    print()
    
    # 评估追问机制是否正常工作
    print("=" * 80)
    print("🎯 测试结果评估")
    print("=" * 80)
    print()
    
    # 判断标准（测试参数配置）
    min_expected_followup_rate = 0.15  # 期望至少15%的问题触发追问
    
    if analysis['followup_count'] == 0:
        print("❌ 失败: 未触发任何追问")
        print("   可能原因:")
        print("   • 候选人回答过于完美")
        print("   • 追问阈值设置过高")
        print("   • 检测逻辑存在问题")
        test_status = "FAILED"
    elif analysis['followup_rate'] < min_expected_followup_rate:
        print(f"⚠️  警告: 追问率偏低 ({analysis['followup_rate']:.1%} < {min_expected_followup_rate:.1%})")
        print("   追问机制可能不够敏感")
        test_status = "WARNING"
    else:
        print(f"✅ 成功: 追问机制正常工作")
        print(f"   触发了 {analysis['followup_count']} 次追问 (追问率: {analysis['followup_rate']:.1%})")
        test_status = "PASSED"
    
    print()
    print(f"面试ID: {result.interview_id}")
    print(f"最终推荐度: {result.recommendation_score}/100")
    print()
    
    return test_status, analysis


def main():
    """主函数"""
    print("\n")
    print("🧪" * 40)
    print("医护场景追问功能专项测试")
    print("🧪" * 40)
    
    try:
        test_status, analysis = test_followup_mechanism()
        
        print("\n" + "=" * 80)
        if test_status == "PASSED":
            print("✅ 测试通过！追问机制工作正常")
        elif test_status == "WARNING":
            print("⚠️  测试完成，但有警告")
        else:
            print("❌ 测试失败！追问机制未正常工作")
        print("=" * 80)
        
        return 0 if test_status == "PASSED" else 1
        
    except Exception as e:
        logger.error(f"测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
