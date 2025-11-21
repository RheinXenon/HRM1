"""
配置模块
用于加载候选人模板、职位配置、公司信息等
"""

import json
import os
from typing import Dict, List
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


__all__ = [
    'load_candidate_template',
    'load_job_config',
    'load_company_config',
    'list_candidate_templates',
    'list_job_configs',
    'list_company_configs'
]
