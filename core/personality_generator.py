"""
性格生成器 - 基于大五人格模型（Big Five Personality Model）
支持外部模型传入的人格评估数据
"""

import random
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from loguru import logger


@dataclass
class PersonalityConfig:
    """
    大五人格配置类（Big Five Personality Traits）
    
    所有维度分数范围: 0.0-1.0
    - Openness (开放性): 好奇心、想象力、对新体验的开放程度
    - Conscientiousness (尽责性): 组织性、可靠性、自律性
    - Extraversion (外向性): 社交性、活力、主导性
    - Agreeableness (宜人性): 合作性、信任、同情心
    - Neuroticism (神经质): 情绪不稳定性、焦虑、易激动（分数越高越不稳定）
    """
    openness: float  # 开放性 (0.0-1.0)
    conscientiousness: float  # 尽责性 (0.0-1.0)
    extraversion: float  # 外向性 (0.0-1.0)
    agreeableness: float  # 宜人性 (0.0-1.0)
    neuroticism: float  # 神经质 (0.0-1.0)
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式"""
        return {
            "openness": round(self.openness, 3),
            "conscientiousness": round(self.conscientiousness, 3),
            "extraversion": round(self.extraversion, 3),
            "agreeableness": round(self.agreeableness, 3),
            "neuroticism": round(self.neuroticism, 3)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PersonalityConfig':
        """从字典创建人格配置"""
        return cls(
            openness=data.get("openness", 0.5),
            conscientiousness=data.get("conscientiousness", 0.5),
            extraversion=data.get("extraversion", 0.5),
            agreeableness=data.get("agreeableness", 0.5),
            neuroticism=data.get("neuroticism", 0.5)
        )
    
    @classmethod
    def from_external_model(cls, model_results: Dict[str, float]) -> 'PersonalityConfig':
        """
        从外部人格评估模型的结果创建人格配置
        
        Args:
            model_results: 外部模型返回的结果，格式为 {label: score}
                          label可以是中文或英文，score范围0-1
        
        Returns:
            PersonalityConfig实例
        """
        # 标签映射（支持中英文）
        label_mapping = {
            # 英文
            "openness": "openness",
            "conscientiousness": "conscientiousness",
            "extraversion": "extraversion",
            "agreeableness": "agreeableness",
            "neuroticism": "neuroticism",
            # 中文
            "开放性": "openness",
            "尽责性": "conscientiousness",
            "外向性": "extraversion",
            "宜人性": "agreeableness",
            "神经质": "neuroticism",
        }
        
        normalized_data = {}
        for label, score in model_results.items():
            # 标准化标签（转小写）
            label_lower = label.lower()
            if label_lower in label_mapping:
                trait = label_mapping[label_lower]
                # 确保分数在0-1范围内
                normalized_data[trait] = max(0.0, min(1.0, float(score)))
            elif label in label_mapping:
                # 中文标签
                trait = label_mapping[label]
                normalized_data[trait] = max(0.0, min(1.0, float(score)))
        
        logger.info(f"📊 从外部模型加载人格数据: {len(normalized_data)}/5 个维度")
        return cls.from_dict(normalized_data)


class PersonalityGenerator:
    """
    大五人格生成器类
    生成符合Big Five模型的人格配置
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        初始化性格生成器
        
        Args:
            seed: 随机种子（用于复现）
        """
        if seed is not None:
            random.seed(seed)
            logger.info(f"🎲 使用随机种子: {seed}")
    
    def generate_random(self, strategy: str = "normal") -> PersonalityConfig:
        """
        生成随机大五人格配置
        
        Args:
            strategy: 生成策略
                - "balanced": 平衡型，所有参数接近0.5
                - "extreme": 极端型，参数偏向极值
                - "uniform": 均匀分布
                - "normal": 正态分布（默认，更真实）
                
        Returns:
            生成的性格配置
        """
        logger.info(f"🎲 生成随机大五人格 [策略: {strategy}]")
        
        traits = {}
        
        for trait_name in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
            if strategy == "balanced":
                # 平衡型：0.5 ± 0.15
                value = self._generate_balanced_float(0.5, 0.0, 1.0)
            elif strategy == "extreme":
                # 极端型：更容易出现极值
                value = self._generate_extreme_float()
            elif strategy == "normal":
                # 正态分布：更符合真实人群
                value = self._generate_normal_float()
            else:  # uniform
                # 均匀分布：完全随机
                value = random.uniform(0.0, 1.0)
            
            traits[trait_name] = value
        
        config = PersonalityConfig(
            openness=traits["openness"],
            conscientiousness=traits["conscientiousness"],
            extraversion=traits["extraversion"],
            agreeableness=traits["agreeableness"],
            neuroticism=traits["neuroticism"]
        )
        
        self._log_personality(config)
        return config
    
    def generate_archetype(self, archetype: str) -> PersonalityConfig:
        """
        生成预设原型大五人格（带随机波动）
        
        Args:
            archetype: 原型名称
                - "confident": 自信型 (高外向性，低神经质)
                - "anxious": 焦虑型 (高神经质，低外向性)
                - "creative": 创造型 (高开放性)
                - "reliable": 可靠型 (高尽责性)
                - "friendly": 友善型 (高宜人性，高外向性)
                - "analytical": 分析型 (高尽责性，高开放性)
                
        Returns:
            生成的性格配置
        """
        logger.info(f"🎭 生成原型大五人格: {archetype}")
        
        # 基于大五人格的原型定义 (O, C, E, A, N)
        archetypes = {
            "confident": {
                "openness": 0.65, "conscientiousness": 0.70, 
                "extraversion": 0.80, "agreeableness": 0.60, "neuroticism": 0.20
            },
            "anxious": {
                "openness": 0.50, "conscientiousness": 0.65,
                "extraversion": 0.30, "agreeableness": 0.55, "neuroticism": 0.75
            },
            "creative": {
                "openness": 0.85, "conscientiousness": 0.55,
                "extraversion": 0.65, "agreeableness": 0.60, "neuroticism": 0.45
            },
            "reliable": {
                "openness": 0.55, "conscientiousness": 0.85,
                "extraversion": 0.50, "agreeableness": 0.70, "neuroticism": 0.30
            },
            "friendly": {
                "openness": 0.60, "conscientiousness": 0.60,
                "extraversion": 0.80, "agreeableness": 0.85, "neuroticism": 0.35
            },
            "analytical": {
                "openness": 0.75, "conscientiousness": 0.80,
                "extraversion": 0.45, "agreeableness": 0.50, "neuroticism": 0.40
            }
        }
        
        if archetype not in archetypes:
            logger.warning(f"未知原型 '{archetype}'，使用 'normal' 策略")
            return self.generate_random("normal")
        
        base = archetypes[archetype]
        
        # 在原型基础上添加 ±0.1 的随机波动
        traits = {}
        for trait_name, base_value in base.items():
            # 添加波动
            value = base_value + random.uniform(-0.1, 0.1)
            # 确保在0-1范围内
            value = max(0.0, min(1.0, value))
            traits[trait_name] = value
        
        config = PersonalityConfig(
            openness=traits["openness"],
            conscientiousness=traits["conscientiousness"],
            extraversion=traits["extraversion"],
            agreeableness=traits["agreeableness"],
            neuroticism=traits["neuroticism"]
        )
        
        self._log_personality(config)
        return config
    
    def _generate_balanced_float(self, center: float, min_val: float, max_val: float) -> float:
        """生成平衡型浮点数值（中心值附近波动）"""
        range_size = max_val - min_val
        deviation = range_size * 0.15  # 15% 波动
        value = center + random.uniform(-deviation, deviation)
        return max(min_val, min(max_val, value))
    
    def _generate_extreme_float(self) -> float:
        """生成极端型浮点数值（更容易出现极值）"""
        # 使用 beta 分布模拟（简化版）
        rand = random.random()
        if rand < 0.3:  # 30% 概率低值 (0.0-0.3)
            return random.uniform(0.0, 0.3)
        elif rand < 0.6:  # 30% 概率高值 (0.7-1.0)
            return random.uniform(0.7, 1.0)
        else:  # 40% 概率中间值 (0.3-0.7)
            return random.uniform(0.3, 0.7)
    
    def _generate_normal_float(self) -> float:
        """生成正态分布浮点数值（更符合真实情况）"""
        center = 0.5
        std_dev = 0.15  # 标准差，大约95%数据在0.2-0.8范围内
        
        value = random.gauss(center, std_dev)
        return max(0.0, min(1.0, value))
    
    def save_personality(
        self,
        config: PersonalityConfig,
        filename: str,
        output_dir: str = "config/candidate_templates/generated"
    ) -> str:
        """
        保存生成的性格配置到文件
        
        Args:
            config: 性格配置
            filename: 文件名（不含扩展名）
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filepath = output_path / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.success(f"💾 性格配置已保存: {filepath}")
        return str(filepath)
    
    def _log_personality(self, config: PersonalityConfig):
        """记录生成的大五人格特征"""
        logger.debug("生成的大五人格参数:")
        logger.debug(f"  开放性 (Openness): {config.openness:.3f}")
        logger.debug(f"  尽责性 (Conscientiousness): {config.conscientiousness:.3f}")
        logger.debug(f"  外向性 (Extraversion): {config.extraversion:.3f}")
        logger.debug(f"  宜人性 (Agreeableness): {config.agreeableness:.3f}")
        logger.debug(f"  神经质 (Neuroticism): {config.neuroticism:.3f}")


def create_random_candidate_config(
    base_template: str = "ideal_candidate",
    personality_strategy: str = "normal",
    name: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建带随机性格的候选人完整配置
    
    Args:
        base_template: 基础模板名称（用于技能和经验）
        personality_strategy: 性格生成策略
        name: 候选人姓名（None则随机生成）
        
    Returns:
        完整的候选人配置字典
    """
    from config import load_candidate_template
    
    # 加载基础模板
    base_config = load_candidate_template(base_template)
    
    # 生成随机性格
    generator = PersonalityGenerator()
    random_personality = generator.generate_random(personality_strategy)
    
    # 替换性格配置
    base_config['profile']['personality'] = random_personality.to_dict()
    
    # 随机生成姓名（可选）
    if name:
        base_config['profile']['name'] = name
    else:
        surnames = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周"]
        given_names = ["明", "华", "强", "伟", "芳", "娜", "静", "丽", "军", "杰"]
        base_config['profile']['name'] = random.choice(surnames) + random.choice(given_names)
    
    logger.info(f"✅ 创建随机候选人: {base_config['profile']['name']}")
    
    return base_config


# 命令行测试工具
if __name__ == "__main__":
    print("🎲 大五人格生成器测试\n")
    
    generator = PersonalityGenerator(seed=42)
    
    strategies = ["balanced", "extreme", "normal", "uniform"]
    
    print("=" * 70)
    print("测试不同生成策略:")
    print("=" * 70)
    
    for strategy in strategies:
        print(f"\n策略: {strategy}")
        config = generator.generate_random(strategy)
        print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 70)
    print("测试原型人格:")
    print("=" * 70)
    
    archetypes = ["confident", "anxious", "creative", "reliable", "friendly", "analytical"]
    
    for archetype in archetypes:
        print(f"\n原型: {archetype}")
        config = generator.generate_archetype(archetype)
        print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 70)
    print("测试从外部模型加载人格数据:")
    print("=" * 70)
    
    # 模拟外部模型返回的数据
    external_results = {
        "openness": 0.75,
        "conscientiousness": 0.82,
        "extraversion": 0.65,
        "agreeableness": 0.58,
        "neuroticism": 0.35
    }
    
    print(f"\n外部模型输入: {external_results}")
    config = PersonalityConfig.from_external_model(external_results)
    print("\n解析后的配置:")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    
    # 测试中文标签
    external_results_cn = {
        "开放性": 0.68,
        "尽责性": 0.72,
        "外向性": 0.55,
        "宜人性": 0.78,
        "神经质": 0.42
    }
    
    print(f"\n\n外部模型输入（中文）: {external_results_cn}")
    config_cn = PersonalityConfig.from_external_model(external_results_cn)
    print("\n解析后的配置:")
    print(json.dumps(config_cn.to_dict(), indent=2, ensure_ascii=False))
