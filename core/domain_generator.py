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
        根据业务描述生成完整的域配置（多步骤生成）
        
        Args:
            business_desc: 业务描述文本
            
        Returns:
            包含所有配置的字典
        """
        try:
            logger.info("🤖 开始多步骤生成域配置...")
            
            # 第一步：生成基础信息和技能体系
            logger.info("📋 步骤1/3: 生成基础信息和技能体系...")
            step1_result = self._generate_domain_and_skills(business_desc)
            
            # 第二步：基于技能体系生成问题模板
            logger.info("❓ 步骤2/3: 生成问题模板...")
            step2_result = self._generate_question_templates(
                business_desc,
                step1_result['domain_config'],
                step1_result['skills_taxonomy']
            )
            
            # 第三步：生成评估信号词
            logger.info("🔍 步骤3/3: 生成评估信号词...")
            step3_result = self._generate_assessment_signals(
                business_desc,
                step1_result['domain_config']
            )
            
            # 合并所有结果
            result = {
                'domain_config': step1_result['domain_config'],
                'skills_taxonomy': step1_result['skills_taxonomy'],
                'question_templates': step2_result,
                'assessment_signals': step3_result
            }
            
            logger.info("✅ 域配置生成成功")
            return result
            
        except Exception as e:
            logger.error(f"❌ 域配置生成失败: {e}")
            raise
    
    def _generate_domain_and_skills(self, business_desc: str) -> Dict:
        """步骤1：生成domain_config和skills_taxonomy"""
        system_prompt = """你是一个专业的面试系统配置专家。根据用户提供的公司和业务信息，生成领域基本信息和技能分类体系。

你需要生成两个部分的配置，以JSON格式返回：

1. domain_config: 领域基本信息
   - domain_id: 领域标识符（小写英文，用下划线连接，简洁明了）
   - domain_name: 领域名称（中文，简洁准确）
   - description: 详细描述（100-200字）
   - applicable_industries: 适用行业列表（6-8个）
   - typical_roles: 典型角色列表（8-12个）
   - typical_projects: 典型项目列表（10-15个）
   - typical_achievements: 典型成就列表（8-12个）

2. skills_taxonomy: 技能分类体系
   - skill_categories: 技能分类字典（**必须是对象，不能是数组！**）
     格式：{"category_id": {"name": "分类名", "skills": ["技能1", "技能2"], "description": "描述"}}
     要求：5-8个技能分类，每个分类包含5-12个技能点
   - soft_skills: 软技能字典（**必须是对象，不能是数组！**）
     格式：{"skill_id": "技能名称"}
     要求：6-10个软技能
   - skill_descriptions: 关键技能的详细描述字典（选3-6个最重要的技能进行描述）

要求：
1. 深入理解行业特点，配置要专业且有深度
2. 技能分类要全面且有层次，覆盖该领域的核心能力
3. 所有内容必须是中文
4. **关键：skill_categories和soft_skills必须使用对象（字典）格式，不能使用数组！**

请严格按照上述JSON格式输出。"""

        user_message = f"""请为以下业务生成领域基本信息和技能分类体系：

{business_desc}

请生成专业、全面的配置。"""
        
        result = self.llm_client.chat_with_json_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        
        # 验证结构
        if 'domain_config' not in result or 'skills_taxonomy' not in result:
            raise ValueError("生成的配置缺少必需字段")
        
        return result
    
    def _generate_question_templates(self, business_desc: str, domain_config: Dict, skills_taxonomy: Dict) -> Dict:
        """步骤2：生成question_templates"""
        system_prompt = """你是一个专业的面试问题设计专家。你需要为面试系统设计问题**模板**，并以JSON格式返回。

⚠️ **关键要求：你生成的是通用模板，不是具体问题！**

模板使用占位符，在实际面试中会被替换为具体内容：
- {skill}: 技能名称
- {mentioned_concept}: 候选人提到的概念
- {term}: 术语
- {vague_statement}: 模糊表述
- {concept}: 概念
- {approach}: 方法
- {technology}: 技术
- {problem}: 问题
- {scenario}: 场景
- {aspect}: 方面
- {requirement}: 需求
- {metric}: 指标

你需要生成三个部分：

1. templates_by_skill_level: 按技能等级分类的问题模板
   - basic: 基础级别（5-8个模板）
     ✅ 正确示例："请介绍一下你对{skill}的理解"
     ❌ 错误示例："请介绍一下你对供应链管理的理解"（太具体）
   - intermediate: 中级（5-8个模板）
     ✅ 正确示例："{skill}在实际项目中遇到过什么问题吗？如何解决的？"
     ❌ 错误示例："供应链系统在实际项目中遇到过什么问题？"（太具体）
   - advanced: 高级（5-8个模板）
     ✅ 正确示例："{skill}的底层原理是什么？"
     ❌ 错误示例："MRP系统的底层原理是什么？"（太具体）

2. followup_templates: 追问模板（每类5-8个）
   - probe_depth: 深入追问，测试真实理解深度
     ✅ 正确："能具体说说{mentioned_concept}的工作原理吗？"
     ❌ 错误："能具体说说安全库存的工作原理吗？"
   - challenge_weakness: 针对模糊回答进行挑战
     ✅ 正确："你刚才说{vague_statement}，能具体解释一下吗？"
     ❌ 错误："你刚才说提升了效率，能具体解释一下吗？"
   - verify_experience: 验证实际经验
     ✅ 正确："你在项目中具体是怎么配置{technology}的？"
     ❌ 错误："你在项目中具体是怎么配置SAP的？"

3. scenario_questions: 场景化问题模板（5-8个）
   ✅ 正确："如果系统出现{problem}，你会如何排查和解决？"
   ❌ 错误："如果系统出现库存数据不一致，你会如何解决？"

**重要：所有模板必须是通用的，使用占位符，不要写成针对具体领域的固定问题！**

请以JSON格式返回，输出格式：
{
  "templates_by_skill_level": {
    "basic": {"description": "基础级别问题", "patterns": ["模板1", "模板2", ...]},
    "intermediate": {"description": "中级问题", "patterns": [...]},
    "advanced": {"description": "高级问题", "patterns": [...]}
  },
  "followup_templates": {
    "probe_depth": {"description": "深入追问，测试真实理解深度", "patterns": [...]},
    "challenge_weakness": {"description": "针对模糊回答进行挑战", "patterns": [...]},
    "verify_experience": {"description": "验证实际经验", "patterns": [...]}
  },
  "scenario_questions": {"description": "场景化问题模板", "patterns": [...]}
}

请严格按照上述要求生成通用模板。"""
        
        # 提取技能列表供参考
        skill_examples = []
        if 'skill_categories' in skills_taxonomy:
            for cat in list(skills_taxonomy['skill_categories'].values())[:2]:
                if 'skills' in cat:
                    skill_examples.extend(cat['skills'][:3])
        
        user_message = f"""领域信息：
名称：{domain_config.get('domain_name', '')}
描述：{domain_config.get('description', '')}

技能示例：{', '.join(skill_examples[:6])}

请为这个领域生成通用的问题模板（使用占位符，不要生成具体问题）。
模板应该适用于该领域的各种技能，通过占位符在实际使用时被替换。"""
        
        result = self.llm_client.chat_with_json_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6
        )
        
        return result
    
    def _generate_assessment_signals(self, business_desc: str, domain_config: Dict) -> Dict:
        """步骤3：生成assessment_signals"""
        system_prompt = """你是一个专业的面试评估专家。根据领域特点，生成评估候选人回答质量的关键信号词，并以JSON格式返回。

你需要生成六类评估信号词：

1. high_level_terms: 高级专业术语（20-30个）
   - 该领域的高级概念、方法论、技术名词
   - 候选人使用这些词汇表明有较深理解

2. technical_metrics: 技术/专业指标（12-18个）
   - 具体的量化指标、性能参数
   - 如：QPS、准确率、周转率等

3. concrete_evidence: 具体证据类词汇（12-15个）
   - 表示候选人在举例、说明具体细节的词汇
   - 如：例如、比如、具体来说、实现、配置等

4. vague_words: 模糊词汇（10-15个）
   - 表示不确定、模糊的词汇
   - 如：大概、应该、可能、好像等

5. weakness_indicators: 露怯关键词（10-15个）
   - 表示知识盲区的词汇
   - 如：不太了解、记不清、不太确定等

6. empty_phrases: 空话套话（8-12个）
   - 没有实质内容的表述
   - 如：我觉得、我认为、非常重要等

请以JSON格式返回，输出格式：
{
  "high_level_terms": {"description": "高级专业术语", "terms": [...]},
  "technical_metrics": {"description": "技术指标", "terms": [...]},
  "concrete_evidence": {"description": "具体证据类词汇", "terms": [...]},
  "vague_words": {"description": "模糊词汇", "terms": [...]},
  "weakness_indicators": {"description": "露怯关键词", "terms": [...]},
  "empty_phrases": {"description": "空话套话", "terms": [...]}
}

请严格按照上述JSON格式输出。"""
        
        user_message = f"""领域信息：
名称：{domain_config.get('domain_name', '')}
描述：{domain_config.get('description', '')}
行业：{', '.join(domain_config.get('applicable_industries', [])[:5])}

请为这个领域生成评估信号词。"""
        
        result = self.llm_client.chat_with_json_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6
        )
        
        return result
    
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
                            "description": "深入追问，测试真实理解深度",
                            "patterns": [
                                "能具体说说{mentioned_concept}的工作原理吗？",
                                "你提到了{term}，能展开讲讲吗？",
                                "为什么选择{approach}而不是其他方案？"
                            ]
                        },
                        "challenge_weakness": {
                            "description": "针对模糊回答进行挑战",
                            "patterns": [
                                "你刚才说{vague_statement}，能具体解释一下吗？",
                                "这个{concept}的关键细节是什么？",
                                "能举个具体的例子说明吗？"
                            ]
                        },
                        "verify_experience": {
                            "description": "验证实际经验",
                            "patterns": [
                                "你在项目中具体是怎么做的？",
                                "遇到{problem}时，排查的步骤是什么？",
                                "能说说具体的指标或数据吗？"
                            ]
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
