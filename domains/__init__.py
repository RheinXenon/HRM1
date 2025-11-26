"""
领域配置加载模块
用于加载不同行业领域的配置（技能分类、评估信号、问题模板等）
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger


DOMAINS_DIR = Path(__file__).parent


class DomainLoader:
    """领域配置加载器"""
    
    def __init__(self, domain_id: str = "tech"):
        """
        初始化领域加载器
        
        Args:
            domain_id: 领域ID（tech, marketing, healthcare等）
        """
        self.domain_id = domain_id
        self.domain_path = DOMAINS_DIR / domain_id
        
        if not self.domain_path.exists():
            logger.warning(f"领域 '{domain_id}' 不存在，使用默认领域 'tech'")
            self.domain_id = "tech"
            self.domain_path = DOMAINS_DIR / "tech"
        
        self._domain_config = None
        self._skills_taxonomy = None
        self._assessment_signals = None
        self._question_templates = None
        
        logger.info(f"加载领域配置: {self.domain_id}")
    
    def _load_json(self, filename: str) -> Dict:
        """加载JSON配置文件"""
        file_path = self.domain_path / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"配置文件解析失败: {file_path}, 错误: {e}")
            return {}
    
    def get_domain_config(self) -> Dict:
        """获取领域配置"""
        if self._domain_config is None:
            self._domain_config = self._load_json("domain_config.json")
        return self._domain_config
    
    def get_skills_taxonomy(self) -> Dict:
        """获取技能分类体系"""
        if self._skills_taxonomy is None:
            self._skills_taxonomy = self._load_json("skills_taxonomy.json")
        return self._skills_taxonomy
    
    def get_assessment_signals(self) -> Dict:
        """获取评估信号词汇"""
        if self._assessment_signals is None:
            self._assessment_signals = self._load_json("assessment_signals.json")
        return self._assessment_signals
    
    def get_question_templates(self) -> Dict:
        """获取问题模板"""
        if self._question_templates is None:
            self._question_templates = self._load_json("question_templates.json")
        return self._question_templates
    
    def get_all_skills(self) -> List[str]:
        """获取所有技能列表"""
        taxonomy = self.get_skills_taxonomy()
        all_skills = []
        
        # 从技能分类中提取所有技能
        for category_data in taxonomy.get("skill_categories", {}).values():
            all_skills.extend(category_data.get("skills", []))
        
        # 添加软技能
        all_skills.extend(taxonomy.get("soft_skills", {}).keys())
        
        return all_skills
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """
        获取技能分类
        
        Returns:
            {category_id: [skill1, skill2, ...], ...}
        """
        taxonomy = self.get_skills_taxonomy()
        categories = {}
        
        for category_id, category_data in taxonomy.get("skill_categories", {}).items():
            categories[category_id] = category_data.get("skills", [])
        
        # 添加软技能类别
        categories["soft_skills"] = list(taxonomy.get("soft_skills", {}).keys())
        
        return categories
    
    def get_high_level_terms(self) -> List[str]:
        """获取高级专业术语列表"""
        signals = self.get_assessment_signals()
        return signals.get("high_level_terms", {}).get("terms", [])
    
    def get_technical_metrics(self) -> List[str]:
        """获取技术/专业指标词汇列表"""
        signals = self.get_assessment_signals()
        # tech领域用technical_metrics，其他领域用concrete_metrics
        return signals.get("technical_metrics", {}).get("terms", []) or \
               signals.get("concrete_metrics", {}).get("terms", [])
    
    def get_concrete_evidence(self) -> List[str]:
        """获取具体证据类词汇列表"""
        signals = self.get_assessment_signals()
        return signals.get("concrete_evidence", {}).get("terms", [])
    
    def get_vague_words(self) -> List[str]:
        """获取模糊词汇列表"""
        signals = self.get_assessment_signals()
        return signals.get("vague_words", {}).get("terms", [])
    
    def get_weakness_indicators(self) -> List[str]:
        """获取露怯关键词列表"""
        signals = self.get_assessment_signals()
        return signals.get("weakness_indicators", {}).get("terms", [])
    
    def get_empty_phrases(self) -> List[str]:
        """获取空话套话列表"""
        signals = self.get_assessment_signals()
        return signals.get("empty_phrases", {}).get("terms", [])


def list_available_domains() -> List[str]:
    """列出所有可用的领域"""
    domains = []
    for path in DOMAINS_DIR.iterdir():
        if path.is_dir() and not path.name.startswith('_'):
            # 检查是否包含必需的配置文件
            if (path / "domain_config.json").exists():
                domains.append(path.name)
    return sorted(domains)


def get_domain_info(domain_id: str) -> Optional[Dict]:
    """
    获取领域基本信息
    
    Args:
        domain_id: 领域ID
        
    Returns:
        领域配置字典，如果不存在返回None
    """
    try:
        loader = DomainLoader(domain_id)
        return loader.get_domain_config()
    except Exception as e:
        logger.error(f"获取领域信息失败: {domain_id}, 错误: {e}")
        return None


__all__ = [
    'DomainLoader',
    'list_available_domains',
    'get_domain_info'
]
