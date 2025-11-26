"""
随机候选人和公司配置生成器
用于生成完全随机的测试数据
"""

import random
from typing import Dict, Any, List, Optional
from loguru import logger
from domains import DomainLoader


class RandomCandidateGenerator:
    """随机候选人生成器"""
    
    # 中文姓名库（保留，因为姓名不需要LLM生成）
    SURNAMES = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周", "徐", "孙", "马", "朱", "胡", "林"]
    GIVEN_NAMES = ["明", "华", "强", "伟", "芳", "娜", "静", "丽", "军", "杰", "涛", "鹏", "磊", "洋", "勇", "峰"]
    
    def __init__(self, seed: Optional[int] = None, domain_id: str = "tech"):
        """
        初始化
        
        Args:
            seed: 随机种子
            domain_id: 领域ID，用于加载对应的技能分类
        """
        if seed:
            random.seed(seed)
        
        # 加载领域配置
        self.domain = DomainLoader(domain_id)
        self.skill_categories = self.domain.get_skill_categories()
    
    def generate_skills(self, level: str = "mid", num_skills: int = None) -> Dict[str, int]:
        """
        生成随机技能评分
        
        Args:
            level: 候选人级别 (junior/mid/senior)
            num_skills: 技能数量，None则随机
            
        Returns:
            技能评分字典
        """
        # 根据级别确定技能范围
        level_ranges = {
            "junior": (3, 6),    # 初级：3-6分
            "mid": (5, 8),       # 中级：5-8分
            "senior": (7, 10)    # 高级：7-10分
        }
        
        min_score, max_score = level_ranges.get(level, (5, 8))
        
        # 随机选择技能数量
        if num_skills is None:
            num_skills = random.randint(8, 12)
        
        skills = {}
        
        # 为每个类别随机选择技能
        for category, skill_list in self.skill_categories.items():
            if not skill_list:
                continue
            # 每个类别选1-3个技能
            selected = random.sample(skill_list, min(random.randint(1, 3), len(skill_list)))
            
            for skill in selected:
                # 使用正态分布生成分数
                center = (min_score + max_score) / 2
                std_dev = (max_score - min_score) / 4
                score = int(random.gauss(center, std_dev))
                score = max(0, min(10, score))  # 限制在0-10
                
                skills[skill] = score
                
                if len(skills) >= num_skills:
                    break
            
            if len(skills) >= num_skills:
                break
        
        # 如果技能不够，补充一些
        all_skills = self.domain.get_all_skills()
        while len(skills) < num_skills and all_skills:
            skill = random.choice(all_skills)
            if skill not in skills:
                score = random.randint(min_score, max_score)
                skills[skill] = score
        
        return dict(list(skills.items())[:num_skills])
    
    def generate_experience(self, level: str = "mid") -> Dict[str, Any]:
        """生成工作经验（从领域配置读取）"""
        level_experience = {
            "junior": (1, 3),
            "mid": (3, 6),
            "senior": (6, 12)
        }
        
        years_range = level_experience.get(level, (3, 6))
        years = random.randint(*years_range)
        
        # 生成项目经历
        num_projects = random.randint(2, 4)
        projects = []
        
        # 从领域配置中读取项目、角色和成就
        typical_projects = self.domain.get_typical_projects()
        typical_roles = self.domain.get_typical_roles()
        typical_achievements = self.domain.get_typical_achievements()
        
        # 如果配置为空，使用默认值
        if not typical_projects:
            typical_projects = ["项目A", "项目B", "项目C"]
        if not typical_roles:
            typical_roles = ["团队成员", "项目负责人"]
        if not typical_achievements:
            typical_achievements = ["完成项目目标", "获得好评"]
        
        for i in range(num_projects):
            duration_months = random.randint(3, 18)
            projects.append({
                "name": random.choice(typical_projects),
                "role": random.choice(typical_roles),
                "duration": f"{duration_months}个月",
                "achievement": random.choice(typical_achievements)
            })
        
        return {
            "years": years,
            "level": level,
            "projects": projects
        }
    
    def generate_knowledge_blind_spots(
        self, 
        skills: Dict[str, int],
        personality: Dict[str, float]
    ) -> Optional[Dict[str, List]]:
        """
        生成知识盲区（基于大五人格特质）
        
        Args:
            skills: 技能评分
            personality: 大五人格配置 (包含 conscientiousness 和 neuroticism)
            
        Returns:
            知识盲区配置
        """
        # 根据大五人格计算自知之明倾向:
        # - 尽责性高 + 神经质低 = 自我认知准确（很少盲区）
        # - 尽责性低 + 神经质低 = 容易过度自信（不懂装懂）
        # - 尽责性高 + 神经质高 = 容易过度谦虚（低估自己）
        
        conscientiousness = personality.get("conscientiousness", 0.5)
        neuroticism = personality.get("neuroticism", 0.5)
        
        # 计算倾向分数
        overconfidence_tendency = (1 - conscientiousness) * (1 - neuroticism)  # 尽责性低、神经质低
        underconfidence_tendency = conscientiousness * neuroticism  # 尽责性高、神经质高
        
        # 高自我认知（尽责性高且神经质适中）
        if conscientiousness > 0.7 and 0.3 < neuroticism < 0.6:
            if random.random() > 0.7:
                return None
        
        blind_spots = {
            "overconfident_areas": [],
            "underconfident_areas": []
        }
        
        # 选择一些技能作为盲区
        skill_items = list(skills.items())
        
        if overconfidence_tendency > 0.5:
            # 容易过度自信
            num_overconfident = random.randint(2, 4)
            for _ in range(num_overconfident):
                if not skill_items:
                    break
                skill, actual_level = random.choice(skill_items)
                skill_items.remove((skill, actual_level))
                
                # 实际能力低，但自我感觉高
                if actual_level <= 6:
                    perceived_level = actual_level + random.randint(2, 4)
                    blind_spots["overconfident_areas"].append({
                        "skill": skill,
                        "actual_level": actual_level,
                        "perceived_level": min(10, perceived_level),
                        "description": f"实际经验有限，但容易高估自己在{skill}方面的能力"
                    })
        
        elif underconfidence_tendency > 0.5:
            # 容易过度谦虚
            num_underconfident = random.randint(1, 3)
            for _ in range(num_underconfident):
                if not skill_items:
                    break
                skill, actual_level = random.choice(skill_items)
                skill_items.remove((skill, actual_level))
                
                if actual_level >= 6:
                    perceived_level = actual_level - random.randint(1, 3)
                    blind_spots["underconfident_areas"].append({
                        "skill": skill,
                        "actual_level": actual_level,
                        "perceived_level": max(0, perceived_level),
                        "description": f"实际能力不错，但对{skill}不够自信"
                    })
        
        else:
            # 中等自知，可能有轻微盲区
            if random.random() > 0.5:
                # 1-2个过度自信
                num_overconfident = random.randint(1, 2)
                for _ in range(num_overconfident):
                    if not skill_items:
                        break
                    skill, actual_level = random.choice(skill_items)
                    skill_items.remove((skill, actual_level))
                    
                    if actual_level <= 7:
                        perceived_level = actual_level + random.randint(1, 2)
                        blind_spots["overconfident_areas"].append({
                            "skill": skill,
                            "actual_level": actual_level,
                            "perceived_level": min(10, perceived_level),
                            "description": f"对{skill}有一定了解，但可能高估自己的深度"
                        })
            else:
                # 1个过度谦虚
                if skill_items:
                    skill, actual_level = random.choice(skill_items)
                    if actual_level >= 7:
                        perceived_level = actual_level - random.randint(1, 2)
                        blind_spots["underconfident_areas"].append({
                            "skill": skill,
                            "actual_level": actual_level,
                            "perceived_level": max(0, perceived_level),
                            "description": f"在{skill}方面有扎实能力，但容易低估自己"
                        })
        
        # 如果没有盲区，返回None
        if not blind_spots["overconfident_areas"] and not blind_spots["underconfident_areas"]:
            return None
        
        return blind_spots
    
    def generate_complete_candidate(
        self,
        level: str = None,
        personality: Dict = None
    ) -> Dict[str, Any]:
        """
        生成完整的随机候选人配置
        
        Args:
            level: 候选人级别，None则随机
            personality: 性格配置，None则随机生成
            
        Returns:
            完整候选人配置
        """
        # 随机级别
        if level is None:
            level = random.choice(["junior", "mid", "senior"])
        
        # 生成姓名
        name = random.choice(self.SURNAMES) + random.choice(self.GIVEN_NAMES)
        
        # 生成技能
        skills = self.generate_skills(level)
        
        # 生成经验
        experience = self.generate_experience(level)
        
        # 生成性格（如果没有提供）
        if personality is None:
            from core.personality_generator import PersonalityGenerator
            pg = PersonalityGenerator()
            personality_config = pg.generate_random("normal")
            personality = personality_config.to_dict()
        
        # 生成知识盲区（基于大五人格特质）
        blind_spots = self.generate_knowledge_blind_spots(skills, personality)
        
        config = {
            "template_name": f"随机候选人-{level}",
            "description": f"随机生成的{level}级候选人",
            "profile": {
                "name": name,
                "skills": skills,
                "experience": experience,
                "personality": personality,
                "knowledge_blind_spots": blind_spots
            }
        }
        
        logger.info(f"✅ 生成随机候选人: {name} ({level}级, {len(skills)}项技能)")
        
        return config


class RandomCompanyGenerator:
    """
    随机公司和职位生成器（使用LLM动态生成）
    
    支持多领域配置（tech/marketing/healthcare）
    """
    
    def __init__(self, seed: Optional[int] = None, domain_id: str = "tech"):
        """
        初始化生成器
        
        Args:
            seed: 随机种子
            domain_id: 领域ID（tech/marketing/healthcare）
        """
        if seed:
            random.seed(seed)
        self.domain_id = domain_id
        
        # 加载领域配置
        self.domain = DomainLoader(domain_id)
        domain_config = self.domain.get_domain_config()
        self.domain_name = domain_config.get("domain_name", domain_id)
        self.description = domain_config.get("description", "")
    
    def generate_company(self) -> Dict[str, Any]:
        """使用LLM生成随机公司配置"""
        from core.llm_client import LLMClient
        
        llm = LLMClient()
        
        prompt = f"""请为{self.domain_name}领域生成一个虚构的公司信息。

要求：
1. 公司名称要符合{self.domain_name}领域特点，听起来真实可信
2. 公司类型要符合该领域的常见分类
3. 简短描述公司的业务范围
4. 企业文化要符合该领域特点

请以JSON格式返回，包含以下字段：
{{
  "name": "公司名称",
  "type": "公司类型",
  "description": "公司简介（一句话）",
  "culture": "企业文化（一句话）"
}}

只返回JSON，不要其他内容。"""

        try:
            response = llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,  # 提高创造性
                max_tokens=300
            )
            
            # 解析JSON
            import json
            import re
            
            content = response.strip()
            # 提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                company_data = json.loads(json_match.group())
                logger.info(f"✅ LLM生成公司: {company_data.get('name', '')}")
                return company_data
            else:
                raise ValueError("未找到有效的JSON")
                
        except Exception as e:
            logger.warning(f"⚠️  LLM生成失败，使用默认值: {e}")
            # 降级方案：使用简单的默认值
            industries = self.domain.get_domain_config().get("applicable_industries", ["公司"])
            company_type = random.choice(industries)
            return {
                "name": f"{company_type}示例公司",
                "type": company_type,
                "description": f"一家专注于{self.domain_name}领域的企业",
                "culture": "追求卓越，以人为本"
            }
    
    def generate_job(self, required_skills: List[str] = None) -> Dict[str, Any]:
        """使用LLM生成随机职位配置"""
        from core.llm_client import LLMClient
        
        # 如果没有指定技能，从domain加载
        if required_skills is None:
            all_skills = self.domain.get_all_skills()
            required_skills = random.sample(all_skills, min(random.randint(5, 8), len(all_skills)))
        
        llm = LLMClient()
        
        # 获取典型角色作为参考
        typical_roles = self.domain.get_typical_roles()
        roles_hint = "、".join(typical_roles[:3]) if typical_roles else "相关职位"
        
        prompt = f"""请为{self.domain_name}领域生成一个职位信息。

参考职位类型：{roles_hint}
要求的技能：{', '.join(required_skills[:5])}

请生成：
1. 职位名称（符合该领域特点）
2. 职位简介（一句话）
3. 3-4条主要职责

请以JSON格式返回：
{{
  "title": "职位名称",
  "description": "职位简介",
  "responsibilities": ["职责1", "职责2", "职责3"]
}}

只返回JSON，不要其他内容。"""

        try:
            response = llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=400
            )
            
            import json
            import re
            
            content = response.strip()
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                job_data = json.loads(json_match.group())
                job_data["required_skills"] = required_skills
                logger.info(f"✅ LLM生成职位: {job_data.get('title', '')}")
                return job_data
            else:
                raise ValueError("未找到有效的JSON")
                
        except Exception as e:
            logger.warning(f"⚠️  LLM生成失败，使用默认值: {e}")
            # 降级方案
            title = random.choice(typical_roles) if typical_roles else f"{self.domain_name}专员"
            return {
                "title": title,
                "required_skills": required_skills,
                "description": f"负责{title}相关工作",
                "responsibilities": [
                    f"完成{self.domain_name}相关的核心工作",
                    "与团队协作，达成业务目标",
                    "持续学习和提升专业能力"
                ]
            }
