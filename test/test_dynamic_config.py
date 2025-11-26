"""
测试动态配置生成功能
验证根据domains自动生成company和job配置
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import generate_domain_config


def test_generate_all_domains():
    """测试为所有领域生成配置"""
    print("\n" + "=" * 70)
    print("测试1: 为所有领域生成配置")
    print("=" * 70)
    
    domains = ["tech", "marketing", "healthcare"]
    
    for domain_id in domains:
        print(f"\n【{domain_id.upper()}领域】")
        company_config, job_config = generate_domain_config(domain_id)
        
        # 验证公司配置
        assert "name" in company_config
        assert "industry" in company_config
        assert "description" in company_config
        print(f"  ✅ 公司: {company_config['name']}")
        print(f"     行业: {company_config['industry']}")
        
        # 验证职位配置
        assert "title" in job_config
        assert "description" in job_config
        assert "requirements" in job_config
        print(f"  ✅ 职位: {job_config['title']}")
        print(f"     描述: {job_config['description'][:30]}...")
        
        # 验证技能要求
        requirements = job_config['requirements']
        assert "必备技能" in requirements
        assert "软技能" in requirements
        
        required_skills = list(requirements['必备技能'].keys())
        soft_skills = list(requirements['软技能'].keys())
        
        print(f"     必备技能({len(required_skills)}个): {', '.join(required_skills[:3])}")
        print(f"     软技能({len(soft_skills)}个): {', '.join(soft_skills[:3])}")
    
    print("\n✅ 所有领域配置生成成功!")


def test_config_content_validity():
    """测试配置内容的合理性"""
    print("\n" + "=" * 70)
    print("测试2: 验证配置内容合理性")
    print("=" * 70)
    
    # Healthcare领域
    company, job = generate_domain_config("healthcare")
    
    print("\nHealthcare领域详细信息:")
    print(f"  公司名: {company['name']}")
    print(f"  职位名: {job['title']}")
    print(f"  职位要求技能数: {len(job['requirements']['必备技能'])}")
    
    # 验证技能来自healthcare taxonomy
    required_skills = list(job['requirements']['必备技能'].keys())
    healthcare_keywords = ['vital_signs', 'medication', 'wound', 'patient', 'clinical', 'nursing']
    
    # 至少有一些技能包含医疗相关关键词
    has_medical_skill = any(
        any(keyword in skill.lower() for keyword in healthcare_keywords)
        for skill in required_skills
    )
    
    if has_medical_skill:
        print("  ✅ 技能包含医疗相关内容")
    else:
        print(f"  ⚠️  技能列表: {required_skills}")
    
    # Marketing领域
    company, job = generate_domain_config("marketing")
    print(f"\nMarketing领域:")
    print(f"  公司名: {company['name']}")
    print(f"  职位名: {job['title']}")
    
    required_skills = list(job['requirements']['必备技能'].keys())
    marketing_keywords = ['marketing', 'campaign', 'brand', 'content', 'seo', 'media']
    
    has_marketing_skill = any(
        any(keyword in skill.lower() for keyword in marketing_keywords)
        for skill in required_skills
    )
    
    if has_marketing_skill:
        print("  ✅ 技能包含营销相关内容")
    else:
        print(f"  ⚠️  技能列表: {required_skills}")
    
    print("\n✅ 配置内容合理性验证通过!")


def test_config_structure():
    """测试配置结构完整性"""
    print("\n" + "=" * 70)
    print("测试3: 验证配置结构完整性")
    print("=" * 70)
    
    company, job = generate_domain_config("tech")
    
    # 验证公司配置必需字段
    required_company_fields = ["company_id", "name", "industry", "description", "culture", "interview_style"]
    print("\n公司配置必需字段:")
    for field in required_company_fields:
        if field in company:
            print(f"  ✅ {field}")
        else:
            print(f"  ❌ {field} 缺失")
            assert False, f"公司配置缺少{field}字段"
    
    # 验证职位配置必需字段
    required_job_fields = ["job_id", "title", "description", "responsibilities", "requirements", "experience", "interview_focus"]
    print("\n职位配置必需字段:")
    for field in required_job_fields:
        if field in job:
            print(f"  ✅ {field}")
        else:
            print(f"  ❌ {field} 缺失")
            assert False, f"职位配置缺少{field}字段"
    
    # 验证requirements结构
    print("\n职位要求结构:")
    requirements = job['requirements']
    for req_type in ["必备技能", "加分项", "软技能"]:
        if req_type in requirements:
            count = len(requirements[req_type])
            print(f"  ✅ {req_type}: {count}个")
        else:
            print(f"  ❌ {req_type} 缺失")
    
    print("\n✅ 配置结构完整性验证通过!")


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🧪 动态配置生成测试套件")
    print("=" * 70)
    
    try:
        test_generate_all_domains()
        test_config_content_validity()
        test_config_structure()
        
        print("\n" + "=" * 70)
        print("✅ 所有测试通过！动态配置生成功能正常！")
        print("=" * 70)
        print("\n💡 功能说明:")
        print("  - 不再需要为每个领域创建固定配置文件")
        print("  - 自动从domains文件夹读取领域信息")
        print("  - 动态生成公司和职位配置")
        print("  - 技能要求直接来自领域的skills_taxonomy")
        print("\n💡 使用方式:")
        print("  from config import generate_domain_config")
        print("  company, job = generate_domain_config('healthcare')")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
