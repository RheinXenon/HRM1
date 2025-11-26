"""
测试领域配置加载功能
验证多领域通用化实施是否成功
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from domains import DomainLoader, list_available_domains, get_domain_info
from core.random_generator import RandomCandidateGenerator


def test_list_domains():
    """测试列出所有可用领域"""
    print("\n" + "="*80)
    print("测试1: 列出所有可用领域")
    print("="*80)
    
    domains = list_available_domains()
    print(f"✅ 找到 {len(domains)} 个领域: {', '.join(domains)}")
    
    assert len(domains) >= 3, "至少应该有3个领域（tech, marketing, healthcare）"
    assert "tech" in domains, "应该包含tech领域"
    assert "marketing" in domains, "应该包含marketing领域"
    assert "healthcare" in domains, "应该包含healthcare领域"
    
    print("✅ 测试通过")
    return domains


def test_load_domain(domain_id: str):
    """测试加载特定领域配置"""
    print(f"\n" + "="*80)
    print(f"测试2: 加载 '{domain_id}' 领域配置")
    print("="*80)
    
    loader = DomainLoader(domain_id)
    
    # 测试获取各项配置
    config = loader.get_domain_config()
    print(f"✅ 领域名称: {config.get('domain_name')}")
    print(f"✅ 描述: {config.get('description')}")
    print(f"✅ 适用行业: {', '.join(config.get('applicable_industries', []))[:60]}...")
    
    taxonomy = loader.get_skills_taxonomy()
    categories = list(taxonomy.get('skill_categories', {}).keys())
    print(f"✅ 技能分类: {', '.join(categories)}")
    
    all_skills = loader.get_all_skills()
    print(f"✅ 总技能数: {len(all_skills)}")
    print(f"   示例技能: {', '.join(all_skills[:5])}...")
    
    signals = loader.get_assessment_signals()
    high_level_terms = loader.get_high_level_terms()
    print(f"✅ 高级术语数: {len(high_level_terms)}")
    print(f"   示例术语: {', '.join(high_level_terms[:5])}...")
    
    vague_words = loader.get_vague_words()
    print(f"✅ 模糊词汇数: {len(vague_words)}")
    
    weakness_indicators = loader.get_weakness_indicators()
    print(f"✅ 露怯关键词数: {len(weakness_indicators)}")
    
    print("✅ 测试通过")


def test_random_generator_with_domain(domain_id: str):
    """测试随机生成器使用领域配置"""
    print(f"\n" + "="*80)
    print(f"测试3: 使用 '{domain_id}' 领域生成随机候选人")
    print("="*80)
    
    generator = RandomCandidateGenerator(seed=42, domain_id=domain_id)
    
    # 生成技能
    skills = generator.generate_skills(level="mid", num_skills=8)
    print(f"✅ 生成了 {len(skills)} 个技能:")
    for skill, level in list(skills.items())[:5]:
        print(f"   - {skill}: {level}/10")
    if len(skills) > 5:
        print(f"   ... 还有 {len(skills) - 5} 个技能")
    
    # 验证生成的技能都在领域配置中
    domain_skills = generator.domain.get_all_skills()
    for skill in skills.keys():
        assert skill in domain_skills, f"生成的技能 '{skill}' 不在领域配置中"
    
    print("✅ 测试通过")


def test_domain_specific_features():
    """测试不同领域的特定功能"""
    print("\n" + "="*80)
    print("测试4: 验证不同领域的差异化配置")
    print("="*80)
    
    # Tech领域
    tech = DomainLoader("tech")
    tech_terms = tech.get_high_level_terms()
    assert "微服务" in tech_terms or "react" in tech_terms, "Tech领域应包含技术术语"
    print(f"✅ Tech领域术语示例: {', '.join(tech_terms[:3])}")
    
    # Marketing领域
    marketing = DomainLoader("marketing")
    marketing_terms = marketing.get_high_level_terms()
    assert "品牌资产" in marketing_terms or "用户画像" in marketing_terms, "Marketing领域应包含营销术语"
    print(f"✅ Marketing领域术语示例: {', '.join(marketing_terms[:3])}")
    
    # Healthcare领域
    healthcare = DomainLoader("healthcare")
    healthcare_terms = healthcare.get_high_level_terms()
    assert "整体护理" in healthcare_terms or "循证护理" in healthcare_terms, "Healthcare领域应包含护理术语"
    print(f"✅ Healthcare领域术语示例: {', '.join(healthcare_terms[:3])}")
    
    # 验证三个领域的术语不同
    assert len(set(tech_terms) & set(marketing_terms)) < 5, "不同领域的术语应该有差异"
    print("✅ 各领域术语已正确分离")
    
    print("✅ 测试通过")


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🧪 领域通用化测试套件")
    print("="*80)
    
    try:
        # 测试1: 列出领域
        domains = test_list_domains()
        
        # 测试2: 加载每个领域
        for domain_id in domains:
            test_load_domain(domain_id)
        
        # 测试3: 测试随机生成器
        for domain_id in ["tech", "marketing", "healthcare"]:
            test_random_generator_with_domain(domain_id)
        
        # 测试4: 测试领域差异化
        test_domain_specific_features()
        
        print("\n" + "="*80)
        print("✅ 所有测试通过！领域通用化实施成功！")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
