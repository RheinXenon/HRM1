"""
域配置生成器
使用LLM自动生成领域配置
"""

import json
from pathlib import Path
from typing import Dict, Optional
from loguru import logger
from core.llm_client import LLMClient


class DomainConfigGenerator:
    """域配置生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.llm_client = LLMClient()
    
    def generate_from_description(self, business_desc: str) -> Dict:
        """
        根据业务描述生成完整的域配置
        
        Args:
            business_desc: 业务描述文本
            
        Returns:
            包含所有配置的字典
        """
        system_prompt = """你是一个专业的面试系统配置专家。根据用户提供的公司和业务信息，生成完整的面试领域配置。

你需要生成四个部分的配置，以JSON格式返回：

1. domain_config: 领域基本信息
   - domain_id: 领域标识符（小写英文，用下划线连接）
   - domain_name: 领域名称（中文）
   - description: 详细描述
   - applicable_industries: 适用行业列表（5-8个）
   - typical_roles: 典型角色列表（5-10个）
   - typical_projects: 典型项目列表（8-12个）
   - typical_achievements: 典型成就列表（6-10个）

2. skills_taxonomy: 技能分类体系
   - skill_categories: 技能分类字典（必须是对象，不能是数组！）
     格式：{"category_id": {"name": "分类名", "skills": ["技能1", "技能2"], "description": "描述"}}
   - soft_skills: 软技能字典（必须是对象，不能是数组！）
     格式：{"skill_id": "技能名称"}
   - skill_descriptions: 关键技能的详细描述字典

3. question_templates: 问题模板
   - templates_by_skill_level: 按技能等级分类（basic, intermediate, advanced）
   - followup_templates: 追问模板（probe_depth, challenge_weakness, verify_experience）
   - scenario_questions: 场景化问题模板

4. assessment_signals: 评估信号词
   - high_level_terms: 高级专业术语（15-30个）
   - technical_metrics/concrete_metrics: 技术/专业指标词汇（10-15个）
   - concrete_evidence: 具体证据类词汇（10-15个）
   - vague_words: 模糊词汇（8-12个）
   - weakness_indicators: 露怯关键词（8-12个）
   - empty_phrases: 空话套话（5-10个）

要求：
1. 深入理解行业特点，配置要专业且有深度
2. 技能分类要全面且有层次，至少5-6个主要分类
3. 问题模板要具体，使用{skill}、{concept}等占位符
4. 评估信号词要精准，贴合该领域的实际情况
5. 所有内容必须是中文
6. **关键：skill_categories和soft_skills必须使用对象（字典）格式，不能使用数组！**

示例结构：
{
  "domain_config": {...},
  "skills_taxonomy": {
    "skill_categories": {
      "backend": {"name": "后端开发", "skills": ["python", "java"], "description": "..."},
      "frontend": {"name": "前端开发", "skills": ["react", "vue"], "description": "..."}
    },
    "soft_skills": {
      "communication": "沟通能力",
      "teamwork": "团队协作"
    }
  },
  "question_templates": {...},
  "assessment_signals": {...}
}

请严格按照上述JSON格式输出。"""

        user_message = f"""请为以下业务生成完整的面试领域配置：

{business_desc}

请生成专业、全面的配置，确保贴合该业务领域的实际情况。"""

        try:
            logger.info("🤖 正在使用AI生成域配置...")
            result = self.llm_client.chat_with_json_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            
            # 验证返回的配置结构
            required_keys = ['domain_config', 'skills_taxonomy', 'question_templates', 'assessment_signals']
            for key in required_keys:
                if key not in result:
                    raise ValueError(f"生成的配置缺少必需字段: {key}")
            
            logger.info("✅ 域配置生成成功")
            return result
            
        except Exception as e:
            logger.error(f"❌ 域配置生成失败: {e}")
            raise
    
    def save_domain_config(self, domain_id: str, configs: Dict) -> bool:
        """
        保存域配置到文件系统
        
        Args:
            domain_id: 域标识符
            configs: 配置字典，包含domain_config, skills_taxonomy等
            
        Returns:
            是否保存成功
        """
        try:
            # 创建域目录
            domain_path = Path(__file__).parent.parent / "domains" / domain_id
            domain_path.mkdir(parents=True, exist_ok=True)
            
            # 保存各个配置文件
            file_mapping = {
                'domain_config': 'domain_config.json',
                'skills_taxonomy': 'skills_taxonomy.json',
                'question_templates': 'question_templates.json',
                'assessment_signals': 'assessment_signals.json'
            }
            
            for config_key, filename in file_mapping.items():
                if config_key in configs:
                    file_path = domain_path / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(configs[config_key], f, ensure_ascii=False, indent=2)
                    logger.debug(f"✅ 已保存: {filename}")
            
            logger.info(f"✅ 域配置已保存到: {domain_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存域配置失败: {e}")
            return False
    
    def load_domain_config(self, domain_id: str) -> Optional[Dict]:
        """
        从文件系统加载域配置
        
        Args:
            domain_id: 域标识符
            
        Returns:
            配置字典，如果不存在返回None
        """
        try:
            domain_path = Path(__file__).parent.parent / "domains" / domain_id
            
            if not domain_path.exists():
                logger.warning(f"域目录不存在: {domain_id}")
                return None
            
            configs = {}
            file_mapping = {
                'domain_config': 'domain_config.json',
                'skills_taxonomy': 'skills_taxonomy.json',
                'question_templates': 'question_templates.json',
                'assessment_signals': 'assessment_signals.json'
            }
            
            for config_key, filename in file_mapping.items():
                file_path = domain_path / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        configs[config_key] = json.load(f)
            
            logger.info(f"✅ 已加载域配置: {domain_id}")
            return configs
            
        except Exception as e:
            logger.error(f"❌ 加载域配置失败: {e}")
            return None
    
    def validate_config(self, configs: Dict) -> tuple[bool, list[str]]:
        """
        验证配置的完整性
        
        Args:
            configs: 配置字典
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必需的顶层键
        required_keys = ['domain_config', 'skills_taxonomy', 'question_templates', 'assessment_signals']
        for key in required_keys:
            if key not in configs:
                errors.append(f"缺少必需配置: {key}")
        
        # 验证 domain_config
        if 'domain_config' in configs:
            dc = configs['domain_config']
            required_dc_keys = ['domain_id', 'domain_name', 'description']
            for key in required_dc_keys:
                if key not in dc or not dc[key]:
                    errors.append(f"domain_config.{key} 不能为空")
        
        # 验证 skills_taxonomy
        if 'skills_taxonomy' in configs:
            st = configs['skills_taxonomy']
            if 'skill_categories' not in st or not st['skill_categories']:
                errors.append("skills_taxonomy.skill_categories 不能为空")
        
        return len(errors) == 0, errors
    
    def get_default_config_template(self, domain_type: str = "general") -> Dict:
        """
        获取默认配置模板
        
        Args:
            domain_type: 模板类型
            
        Returns:
            配置模板
        """
        templates = {
            "general": {
                "domain_config": {
                    "domain_id": "new_domain",
                    "domain_name": "新领域",
                    "description": "请填写领域描述",
                    "applicable_industries": ["行业1", "行业2"],
                    "typical_roles": ["角色1", "角色2"],
                    "typical_projects": ["项目1", "项目2"],
                    "typical_achievements": ["成就1", "成就2"]
                },
                "skills_taxonomy": {
                    "skill_categories": {
                        "category1": {
                            "name": "分类1",
                            "skills": ["技能1", "技能2"],
                            "description": "分类描述"
                        }
                    },
                    "soft_skills": {
                        "communication": "沟通能力",
                        "teamwork": "团队协作"
                    },
                    "skill_descriptions": {}
                },
                "question_templates": {
                    "templates_by_skill_level": {
                        "basic": {
                            "description": "基础级别问题",
                            "patterns": ["请介绍一下你对{skill}的理解"]
                        },
                        "intermediate": {
                            "description": "中级问题",
                            "patterns": ["{skill}在实际项目中遇到过什么问题？"]
                        },
                        "advanced": {
                            "description": "高级问题",
                            "patterns": ["{skill}的底层原理是什么？"]
                        }
                    },
                    "followup_templates": {
                        "probe_depth": {
                            "description": "深入追问",
                            "patterns": ["能具体说说{mentioned_concept}的工作原理吗？"]
                        }
                    },
                    "scenario_questions": {
                        "description": "场景化问题",
                        "patterns": ["如果系统出现{problem}，你会如何解决？"]
                    }
                },
                "assessment_signals": {
                    "high_level_terms": {
                        "description": "高级专业术语",
                        "terms": ["专业术语1", "专业术语2"]
                    },
                    "technical_metrics": {
                        "description": "技术指标",
                        "terms": ["指标1", "指标2"]
                    },
                    "concrete_evidence": {
                        "description": "具体证据",
                        "terms": ["例如", "比如", "具体来说"]
                    },
                    "vague_words": {
                        "description": "模糊词汇",
                        "terms": ["大概", "应该", "可能"]
                    },
                    "weakness_indicators": {
                        "description": "露怯关键词",
                        "terms": ["不太了解", "记不清"]
                    },
                    "empty_phrases": {
                        "description": "空话套话",
                        "terms": ["我觉得", "我认为"]
                    }
                }
            }
        }
        
        return templates.get(domain_type, templates["general"])
