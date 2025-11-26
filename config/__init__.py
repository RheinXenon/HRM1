"""
配置模块
用于加载候选人模板、职位配置、公司信息等
支持基于domains动态生成面试配置
"""

import json
import os
import random
from typing import Dict, List, Tuple
from pathlib import Path


CONFIG_DIR = Path(__file__).parent


def load_candidate_template(template_name: str) -> Dict:
    """
    加载候选人模板
    
    Args:
        template_name: 模板名称（不含.json后缀）
        
    Returns:
        候选人配置字典
    """
    template_path = CONFIG_DIR / "candidate_templates" / f"{template_name}.json"
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_job_config(job_name: str) -> Dict:
    """
    加载职位配置
    
    Args:
        job_name: 职位配置文件名（不含.json后缀）
        
    Returns:
        职位配置字典
    """
    job_path = CONFIG_DIR / "jobs" / f"{job_name}.json"
    with open(job_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_company_config(company_name: str) -> Dict:
    """
    加载公司信息配置
    
    Args:
        company_name: 公司配置文件名（不含.json后缀）
        
    Returns:
        公司信息字典
    """
    company_path = CONFIG_DIR / "companies" / f"{company_name}.json"
    with open(company_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_candidate_templates() -> List[str]:
    """列出所有可用的候选人模板"""
    templates_dir = CONFIG_DIR / "candidate_templates"
    return [f.stem for f in templates_dir.glob("*.json")]


def list_job_configs() -> List[str]:
    """列出所有可用的职位配置"""
    jobs_dir = CONFIG_DIR / "jobs"
    return [f.stem for f in jobs_dir.glob("*.json")]


def list_company_configs() -> List[str]:
    """列出所有可用的公司配置"""
    companies_dir = CONFIG_DIR / "companies"
    return [f.stem for f in companies_dir.glob("*.json")]


def generate_domain_config(domain_id: str = "tech") -> Tuple[Dict, Dict]:
    """
    根据领域ID动态生成公司和职位配置
    
    Args:
        domain_id: 领域ID（tech/marketing/healthcare等）
        
    Returns:
        (company_config, job_config) 元组
    """
    from domains import DomainLoader
    
    # 加载领域配置（使用单例模式）
    domain_loader = DomainLoader.get_instance(domain_id)
    domain_config = domain_loader.get_domain_config()
    skills_taxonomy = domain_loader.get_skills_taxonomy()
    
    # 从domain_config获取领域信息
    domain_name = domain_config.get("domain_name", domain_id)
    industries = domain_config.get("applicable_industries", [])
    roles = domain_config.get("typical_roles", [])
    
    # 动态生成公司名称（根据领域特点）
    company_name_map = {
        "tech": "创新科技有限公司",
        "marketing": "盛世广告传媒",
        "healthcare": "仁心医疗机构"
    }
    company_name = company_name_map.get(
        domain_id, 
        f"{industries[0]}{random.choice(['集团', '公司', '中心', '机构'])}" if industries else "专业服务公司"
    )
    
    # 动态生成公司配置
    company_config = {
        "company_id": f"{domain_id}_company_001",
        "name": company_name,
        "industry": domain_name,
        "size": "100-500人",
        "stage": "成熟发展期",
        "location": "市中心",
        "description": f"一家专注于{domain_name}的优秀公司，致力于为客户提供专业服务。",
        "culture": {
            "values": ["专业敬业", "持续学习", "团队协作", "追求卓越"],
            "work_style": "注重专业能力与团队配合",
            "benefits": ["有竞争力的薪资", "完善的培训体系", "良好的职业发展", "五险一金"]
        },
        "interview_style": "注重实际能力和经验，看重专业素养"
    }
    
    # 选择一个典型角色作为职位
    job_title = roles[0] if roles else f"{domain_name}专员"
    
    # 从技能分类中提取技能要求
    skill_categories = skills_taxonomy.get("skill_categories", {})
    soft_skills = skills_taxonomy.get("soft_skills", {})
    
    # 构建技能要求（选择主要技能）
    requirements = {"必备技能": {}, "加分项": {}, "软技能": {}}
    
    # 从每个硬技能类别中选择2-3个技能作为必备
    for category_id, category_data in list(skill_categories.items())[:2]:
        skills_list = category_data.get("skills", [])
        for skill in skills_list[:3]:
            requirements["必备技能"][skill] = random.randint(6, 8)
    
    # 从其他类别中选择技能作为加分项
    for category_id, category_data in list(skill_categories.items())[2:4]:
        skills_list = category_data.get("skills", [])
        for skill in skills_list[:2]:
            requirements["加分项"][skill] = random.randint(5, 7)
    
    # 添加软技能
    for soft_skill in list(soft_skills.keys())[:4]:
        requirements["软技能"][soft_skill] = random.randint(6, 8)
    
    # 动态生成职位配置
    job_config = {
        "job_id": f"{domain_id}_job_001",
        "title": job_title,
        "department": "业务部门",
        "location": "市中心",
        "employment_type": "全职",
        "salary_range": "面议",
        "description": f"我们正在寻找一位优秀的{job_title}，负责相关业务的开展和管理。",
        "responsibilities": [
            f"负责{domain_name}相关的核心业务",
            "与团队协作完成项目目标",
            "持续学习和提升专业能力",
            "参与业务流程优化"
        ],
        "requirements": requirements,
        "experience": {
            "min_years": 3,
            "preferred_level": "mid",
            "industry": industries[:3]
        },
        "interview_focus": [
            "专业技能和知识",
            "实际工作经验",
            "问题解决能力",
            "团队协作能力"
        ]
    }
    
    return company_config, job_config


__all__ = [
    'load_candidate_template',
    'load_job_config',
    'load_company_config',
    'list_candidate_templates',
    'list_job_configs',
    'list_company_configs',
    'generate_domain_config'
]
