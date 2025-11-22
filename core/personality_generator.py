"""
性格生成器
随机生成候选人的性格特质参数
"""

import random
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from loguru import logger


@dataclass
class PersonalityConfig:
    """性格配置类"""
    communication: Dict[str, int]
    response: Dict[str, int]
    emotion: Dict[str, int]
    self_perception: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "communication": self.communication,
            "response": self.response,
            "emotion": self.emotion,
            "self_perception": self.self_perception
        }


class PersonalityGenerator:
    """性格生成器类"""
    
    # 性格维度定义及其合理范围
    DIMENSIONS = {
        "communication": {
            "verbose": (20, 90),      # 啰嗦程度：20-90
            "technical": (30, 95)     # 技术用词：30-95
        },
        "response": {
            "confidence": (30, 95),         # 自信度：30-95
            "detail_orientation": (30, 90), # 细节程度：30-90
            "storytelling": (20, 85)        # 叙事能力：20-85
        },
        "emotion": {
            "nervousness": (5, 70),    # 紧张度：5-70
            "enthusiasm": (30, 95)     # 热情度：30-95
        },
        "self_perception": {
            "self_awareness": (20, 95)  # 自知之明：20-95，低值易不懂装懂，高值易过度谦虚
        }
    }
    
    def __init__(self, seed: Optional[int] = None):
        """
        初始化性格生成器
        
        Args:
            seed: 随机种子（用于复现）
        """
        if seed is not None:
            random.seed(seed)
            logger.info(f"🎲 使用随机种子: {seed}")
    
    def generate_random(self, strategy: str = "balanced") -> PersonalityConfig:
        """
        生成随机性格
        
        Args:
            strategy: 生成策略
                - "balanced": 平衡型，所有参数接近中间值
                - "extreme": 极端型，参数偏向极值
                - "uniform": 均匀分布
                - "normal": 正态分布（更真实）
                
        Returns:
            生成的性格配置
        """
        logger.info(f"🎲 生成随机性格 [策略: {strategy}]")
        
        personality = {}
        
        for category, dimensions in self.DIMENSIONS.items():
            personality[category] = {}
            for dim_name, (min_val, max_val) in dimensions.items():
                if strategy == "balanced":
                    # 平衡型：中心值 ± 20%波动
                    center = (min_val + max_val) // 2
                    value = self._generate_balanced(center, min_val, max_val)
                    
                elif strategy == "extreme":
                    # 极端型：更容易出现极值
                    value = self._generate_extreme(min_val, max_val)
                    
                elif strategy == "normal":
                    # 正态分布：更符合真实人群
                    value = self._generate_normal(min_val, max_val)
                    
                else:  # uniform
                    # 均匀分布：完全随机
                    value = random.randint(min_val, max_val)
                
                personality[category][dim_name] = value
        
        config = PersonalityConfig(
            communication=personality["communication"],
            response=personality["response"],
            emotion=personality["emotion"],
            self_perception=personality["self_perception"]
        )
        
        self._log_personality(config)
        return config
    
    def generate_archetype(self, archetype: str) -> PersonalityConfig:
        """
        生成预设原型性格（带随机波动）
        
        Args:
            archetype: 原型名称
                - "confident": 自信型
                - "nervous": 紧张型
                - "technical": 技术型
                - "storyteller": 叙事型
                - "enthusiastic": 热情型
                - "reserved": 保守型
                
        Returns:
            生成的性格配置
        """
        logger.info(f"🎭 生成原型性格: {archetype}")
        
        archetypes = {
            "confident": {
                "communication": {"verbose": 60, "technical": 75},
                "response": {"confidence": 90, "detail_orientation": 70, "storytelling": 60},
                "emotion": {"nervousness": 10, "enthusiasm": 80},
                "self_perception": {"self_awareness": 50}  # 中等自知，容易不懂装懂
            },
            "nervous": {
                "communication": {"verbose": 40, "technical": 50},
                "response": {"confidence": 40, "detail_orientation": 60, "storytelling": 40},
                "emotion": {"nervousness": 65, "enthusiasm": 45},
                "self_perception": {"self_awareness": 80}  # 高自知，容易过度谦虚
            },
            "technical": {
                "communication": {"verbose": 70, "technical": 90},
                "response": {"confidence": 75, "detail_orientation": 85, "storytelling": 50},
                "emotion": {"nervousness": 25, "enthusiasm": 65},
                "self_perception": {"self_awareness": 70}
            },
            "storyteller": {
                "communication": {"verbose": 80, "technical": 55},
                "response": {"confidence": 70, "detail_orientation": 60, "storytelling": 85},
                "emotion": {"nervousness": 20, "enthusiasm": 85},
                "self_perception": {"self_awareness": 70}
            },
            "enthusiastic": {
                "communication": {"verbose": 75, "technical": 65},
                "response": {"confidence": 80, "detail_orientation": 60, "storytelling": 70},
                "emotion": {"nervousness": 15, "enthusiasm": 92},
                "self_perception": {"self_awareness": 60}
            },
            "reserved": {
                "communication": {"verbose": 35, "technical": 70},
                "response": {"confidence": 55, "detail_orientation": 75, "storytelling": 45},
                "emotion": {"nervousness": 40, "enthusiasm": 40},
                "self_perception": {"self_awareness": 75}
            }
        }
        
        if archetype not in archetypes:
            logger.warning(f"未知原型 '{archetype}'，使用 'balanced' 策略")
            return self.generate_random("balanced")
        
        base = archetypes[archetype]
        
        # 在原型基础上添加 ±15 的随机波动
        personality = {}
        for category in ["communication", "response", "emotion", "self_perception"]:
            personality[category] = {}
            for dim_name, base_value in base[category].items():
                # 获取合理范围
                min_val, max_val = self.DIMENSIONS[category][dim_name]
                # 添加波动
                value = base_value + random.randint(-15, 15)
                # 确保在合理范围内
                value = max(min_val, min(max_val, value))
                personality[category][dim_name] = value
        
        config = PersonalityConfig(
            communication=personality["communication"],
            response=personality["response"],
            emotion=personality["emotion"],
            self_perception=personality["self_perception"]
        )
        
        self._log_personality(config)
        return config
    
    def _generate_balanced(self, center: int, min_val: int, max_val: int) -> int:
        """生成平衡型数值（中心值附近波动）"""
        range_size = max_val - min_val
        deviation = int(range_size * 0.2)  # 20% 波动
        value = center + random.randint(-deviation, deviation)
        return max(min_val, min(max_val, value))
    
    def _generate_extreme(self, min_val: int, max_val: int) -> int:
        """生成极端型数值（更容易出现极值）"""
        # 使用 beta 分布模拟（简化版）
        rand = random.random()
        if rand < 0.3:  # 30% 概率低值
            return random.randint(min_val, min_val + (max_val - min_val) // 3)
        elif rand < 0.6:  # 30% 概率高值
            return random.randint(min_val + 2 * (max_val - min_val) // 3, max_val)
        else:  # 40% 概率中间值
            return random.randint(min_val + (max_val - min_val) // 3, 
                                 min_val + 2 * (max_val - min_val) // 3)
    
    def _generate_normal(self, min_val: int, max_val: int) -> int:
        """生成正态分布数值（更符合真实情况）"""
        center = (min_val + max_val) / 2
        std_dev = (max_val - min_val) / 6  # 99.7% 数据在 ±3σ 内
        
        value = int(random.gauss(center, std_dev))
        return max(min_val, min(max_val, value))
    
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
        """记录生成的性格特征"""
        logger.debug("生成的性格参数:")
        logger.debug(f"  沟通: verbose={config.communication['verbose']}, "
                    f"technical={config.communication['technical']}")
        logger.debug(f"  回答: confidence={config.response['confidence']}, "
                    f"detail={config.response['detail_orientation']}, "
                    f"storytelling={config.response['storytelling']}")
        logger.debug(f"  情绪: nervousness={config.emotion['nervousness']}, "
                    f"enthusiasm={config.emotion['enthusiasm']}")
        logger.debug(f"  自我认知: self_awareness={config.self_perception['self_awareness']}")


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
    print("🎲 性格生成器测试\n")
    
    generator = PersonalityGenerator(seed=42)
    
    strategies = ["balanced", "extreme", "normal", "uniform"]
    
    print("=" * 60)
    print("测试不同生成策略:")
    print("=" * 60)
    
    for strategy in strategies:
        print(f"\n策略: {strategy}")
        config = generator.generate_random(strategy)
        print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试原型性格:")
    print("=" * 60)
    
    archetypes = ["confident", "nervous", "technical", "storyteller"]
    
    for archetype in archetypes:
        print(f"\n原型: {archetype}")
        config = generator.generate_archetype(archetype)
        print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
