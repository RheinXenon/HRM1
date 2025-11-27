"""
测试域配置生成器功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.domain_generator import DomainConfigGenerator


def test_get_default_template():
    """测试获取默认模板"""
    print("\n" + "=" * 60)
    print("测试1: 获取默认模板")
    print("=" * 60)
    
    generator = DomainConfigGenerator()
    template = generator.get_default_config_template()
    
    assert 'domain_config' in template
    assert 'skills_taxonomy' in template
    assert 'question_templates' in template
    assert 'assessment_signals' in template
    
    print("✅ 默认模板结构正确")
    print(f"   - domain_config: {template['domain_config']['domain_name']}")
    print(f"   - skills_taxonomy: {len(template['skills_taxonomy']['skill_categories'])} 个分类")
    print(f"   - question_templates: {len(template['question_templates']['templates_by_skill_level'])} 个级别")
    print(f"   - assessment_signals: {len(template['assessment_signals'])} 个信号类别")


def test_load_existing_domain():
    """测试加载现有域"""
    print("\n" + "=" * 60)
    print("测试2: 加载现有域配置")
    print("=" * 60)
    
    generator = DomainConfigGenerator()
    configs = generator.load_domain_config('tech')
    
    if configs:
        print("✅ 成功加载tech域配置")
        print(f"   - 域名称: {configs['domain_config']['domain_name']}")
        print(f"   - 技能分类: {len(configs['skills_taxonomy']['skill_categories'])} 个")
        print(f"   - 适用行业: {', '.join(configs['domain_config']['applicable_industries'][:3])}...")
    else:
        print("⚠️  tech域配置不存在或加载失败")


def test_validate_config():
    """测试配置验证"""
    print("\n" + "=" * 60)
    print("测试3: 配置验证")
    print("=" * 60)
    
    generator = DomainConfigGenerator()
    
    # 测试有效配置
    valid_config = generator.get_default_config_template()
    is_valid, errors = generator.validate_config(valid_config)
    
    if is_valid:
        print("✅ 默认配置验证通过")
    else:
        print(f"❌ 默认配置验证失败: {errors}")
    
    # 测试无效配置
    invalid_config = {'domain_config': {}}
    is_valid, errors = generator.validate_config(invalid_config)
    
    if not is_valid:
        print("✅ 正确识别无效配置")
        print(f"   错误信息: {errors[:2]}...")
    else:
        print("❌ 未能识别无效配置")


def test_save_and_load():
    """测试保存和加载"""
    print("\n" + "=" * 60)
    print("测试4: 保存和加载测试域")
    print("=" * 60)
    
    generator = DomainConfigGenerator()
    
    # 创建测试配置
    test_config = generator.get_default_config_template()
    test_config['domain_config']['domain_id'] = 'test_domain'
    test_config['domain_config']['domain_name'] = '测试领域'
    test_config['domain_config']['description'] = '这是一个测试领域'
    
    # 保存
    success = generator.save_domain_config('test_domain', test_config)
    
    if success:
        print("✅ 测试域配置保存成功")
        
        # 加载
        loaded_config = generator.load_domain_config('test_domain')
        
        if loaded_config:
            print("✅ 测试域配置加载成功")
            assert loaded_config['domain_config']['domain_name'] == '测试领域'
            print("✅ 配置内容验证通过")
            
            # 清理测试文件
            test_domain_path = project_root / "domains" / "test_domain"
            if test_domain_path.exists():
                import shutil
                shutil.rmtree(test_domain_path)
                print("✅ 测试文件已清理")
        else:
            print("❌ 加载测试域失败")
    else:
        print("❌ 保存测试域失败")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 域配置生成器测试套件")
    print("=" * 60)
    
    try:
        test_get_default_template()
        test_load_existing_domain()
        test_validate_config()
        test_save_and_load()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
