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
    
    # 姓氏和名字库
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
        """生成工作经验"""
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
        
        project_names = [
            "企业管理系统", "电商平台", "数据分析平台", "在线教育系统",
            "物流管理系统", "金融交易系统", "社交媒体应用", "智能推荐引擎"
        ]
        
        roles = ["后端开发", "全栈开发", "技术负责人", "架构师", "核心开发"]
        
        for i in range(num_projects):
            duration_months = random.randint(3, 18)
            projects.append({
                "name": random.choice(project_names),
                "role": random.choice(roles),
                "duration": f"{duration_months}个月",
                "achievement": "完成核心功能开发" if random.random() > 0.5 else "主导系统架构设计"
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
    随机公司和职位生成器
    
    注意：此类主要用于测试，生产环境请使用 config.generate_domain_config()
    支持多领域配置（tech/marketing/healthcare）
    """
    
    # 各领域的公司类型
    COMPANY_TYPES_BY_DOMAIN = {
        "tech": [
            "互联网创业公司", "传统软件企业", "金融科技公司", 
            "电商平台", "游戏公司", "人工智能企业"
        ],
        "marketing": [
            "广告代理公司", "品牌咨询公司", "数字营销公司",
            "公关公司", "媒体公司", "内容创作公司"
        ],
        "healthcare": [
            "综合医院", "专科医院", "社区卫生中心",
            "康复中心", "健康管理公司", "养老服务机构"
        ]
    }
    
    # 各领域的职位名称
    JOB_TITLES_BY_DOMAIN = {
        "tech": [
            "高级后端工程师", "全栈工程师", "系统架构师",
            "技术负责人", "后端开发工程师", "平台开发工程师"
        ],
        "marketing": [
            "营销经理", "品牌专员", "内容运营",
            "数字营销专家", "社交媒体经理", "市场策划"
        ],
        "healthcare": [
            "注册护士", "护理主管", "健康管理师",
            "康复治疗师", "临床护理专家", "护理协调员"
        ]
    }
    
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
        self.company_types = self.COMPANY_TYPES_BY_DOMAIN.get(domain_id, self.COMPANY_TYPES_BY_DOMAIN["tech"])
        self.job_titles = self.JOB_TITLES_BY_DOMAIN.get(domain_id, self.JOB_TITLES_BY_DOMAIN["tech"])
    
    def generate_company(self) -> Dict[str, Any]:
        """生成随机公司配置（基于领域）"""
        company_type = random.choice(self.company_types)
        
        # 各领域的公司名称池
        company_names_by_domain = {
            "tech": {
                "互联网创业公司": ["极客科技", "创新网络", "未来互联"],
                "传统软件企业": ["中软国际", "东软集团", "用友网络"],
                "金融科技公司": ["蚂蚁金服", "京东数科", "平安科技"],
                "电商平台": ["阿里巴巴", "京东", "拼多多"],
                "游戏公司": ["腾讯游戏", "网易游戏", "米哈游"],
                "人工智能企业": ["商汤科技", "旷视科技", "依图科技"]
            },
            "marketing": {
                "广告代理公司": ["盛世广告", "博雅公关", "智威汤逊"],
                "品牌咨询公司": ["品牌方略", "华与华", "特劳特"],
                "数字营销公司": ["数字一百", "易传媒", "蓝色光标"],
                "公关公司": ["万博宣伟", "爱德曼", "奥美"],
                "媒体公司": ["分众传媒", "新潮传媒", "凤凰传媒"],
                "内容创作公司": ["二更", "一条", "十点读书"]
            },
            "healthcare": {
                "综合医院": ["市第一人民医院", "中心医院", "协和医院"],
                "专科医院": ["肿瘤医院", "儿童医院", "妇产医院"],
                "社区卫生中心": ["社区医疗中心", "街道卫生服务中心", "基层卫生院"],
                "康复中心": ["康复医疗中心", "疗养康复院", "护理康复中心"],
                "健康管理公司": ["美年大健康", "爱康国宾", "慈铭体检"],
                "养老服务机构": ["太阳城养老", "亲和源", "泰康之家"]
            }
        }
        
        domain_names = company_names_by_domain.get(self.domain_id, company_names_by_domain["tech"])
        name = random.choice(domain_names.get(company_type, [f"{company_type}示例"]))
        
        # 各领域的企业文化
        culture_by_domain = {
            "tech": [
                "扁平化管理，鼓励创新",
                "注重技术深度，追求卓越",
                "快速迭代，拥抱变化"
            ],
            "marketing": [
                "创意驱动，追求卓越",
                "以客户为中心，结果导向",
                "开放协作，快速响应"
            ],
            "healthcare": [
                "以患者为中心，关爱生命",
                "专业严谨，持续学习",
                "团队协作，守护健康"
            ]
        }
        
        return {
            "name": name,
            "type": company_type,
            "description": f"一家专注于{company_type}领域的企业",
            "culture": random.choice(culture_by_domain.get(self.domain_id, culture_by_domain["tech"]))
        }
    
    def generate_job(self, required_skills: List[str] = None) -> Dict[str, Any]:
        """生成随机职位配置（基于领域）"""
        title = random.choice(self.job_titles)
        
        # 如果没有指定技能，从domain加载
        if required_skills is None:
            from domains import DomainLoader
            domain_loader = DomainLoader(self.domain_id)
            all_skills = domain_loader.get_all_skills()
            required_skills = random.sample(all_skills, min(random.randint(5, 8), len(all_skills)))
        
        # 各领域的职责描述
        responsibilities_by_domain = {
            "tech": [
                "参与系统架构设计和优化",
                "编写高质量、可维护的代码",
                "解决复杂技术问题"
            ],
            "marketing": [
                "制定和执行营销策略",
                "管理品牌推广和市场活动",
                "分析市场数据并优化营销效果"
            ],
            "healthcare": [
                "提供专业的护理和健康服务",
                "执行医疗护理计划和健康评估",
                "确保患者安全和服务质量"
            ]
        }
        
        return {
            "title": title,
            "required_skills": required_skills,
            "description": f"负责{title}相关工作",
            "responsibilities": responsibilities_by_domain.get(self.domain_id, responsibilities_by_domain["tech"])
        }
