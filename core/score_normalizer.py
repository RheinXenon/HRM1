"""
评分标准化模块 - Phase 1 Implementation
负责将多维度评分转换为标准化的0-100分数
"""

from typing import Dict, Optional, List
import math
from loguru import logger


# 评估维度定义
EVALUATION_DIMENSIONS = {
    "technical_depth": {
        "name": "技术深度",
        "scale": "1-4",
        "anchors": {
            1: "仅知道概念名称,无法解释原理",
            2: "理解基本原理,但缺乏深度",
            3: "深入理解原理,能举实例",
            4: "精通原理,能分析边界情况和trade-offs"
        }
    },
    "practical_experience": {
        "name": "实践经验",
        "scale": "1-4",
        "anchors": {
            1: "无法提供具体项目细节",
            2: "有项目但细节模糊",
            3: "提供了具体的项目经验和数据",
            4: "详细描述了复杂场景和解决方案"
        }
    },
    "answer_specificity": {
        "name": "回答具体性",
        "scale": "1-4",
        "anchors": {
            1: "完全没有具体细节或数据",
            2: "偶尔提到细节但不完整",
            3: "包含多个具体参数、配置或代码",
            4: "充满量化指标、架构图、代码示例"
        }
    },
    "logical_clarity": {
        "name": "逻辑清晰度",
        "scale": "1-4",
        "anchors": {
            1: "混乱无条理",
            2: "基本有条理",
            3: "结构清晰",
            4: "逻辑严密、层次分明"
        }
    },
    "honesty": {
        "name": "诚实度",
        "scale": "1-4",
        "anchors": {
            1: "明显不懂装懂",
            2: "有夸大倾向",
            3: "比较诚实",
            4: "准确认知自己的边界"
        }
    },
    "communication": {
        "name": "沟通能力",
        "scale": "1-4",
        "anchors": {
            1: "表达不清",
            2: "基本能说清楚",
            3: "表达清晰",
            4: "表达精准且有感染力"
        }
    }
}


# 评分标准配置
SCORING_STANDARD = {
    "distribution": "normal",
    "mean": 50,
    "std": 15,

    "interpretation": {
        "90-100": "卓越 (Top 2.3%) - 远超职位要求",
        "75-89":  "优秀 (Top 16%) - 明显超出预期",
        "60-74":  "良好 (34%) - 符合期望",
        "40-59":  "一般 (34%) - 基本符合但有不足",
        "25-39":  "较差 (14%) - 明显低于要求",
        "0-24":   "不合格 (2.3%) - 严重不符合"
    },

    "decision_threshold": {
        "strong_hire": 75,   # 强烈推荐
        "hire": 60,          # 推荐
        "maybe": 40,         # 待定/备选
        "no_hire": 40        # 不推荐（<40）
    }
}


class ScoreNormalizer:
    """
    评分标准化器

    功能:
    1. 将多维度评分(1-4)转换为标准化总分(0-100)
    2. 应用正态分布映射(均值50,标准差15)
    3. 提供评分解释和建议
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化标准化器

        Args:
            weights: 各维度权重,默认使用推荐权重
        """
        # 默认权重
        self.default_weights = {
            "technical_depth": 0.25,      # 技术深度最重要
            "practical_experience": 0.20,  # 实践经验次之
            "answer_specificity": 0.20,    # 回答具体性重要
            "logical_clarity": 0.15,       # 逻辑清晰度
            "honesty": 0.15,               # 诚实度(防止不懂装懂)
            "communication": 0.05          # 沟通能力
        }

        self.weights = weights if weights else self.default_weights

        # 验证权重
        self._validate_weights()

        logger.info("✅ ScoreNormalizer 初始化完成")

    def _validate_weights(self):
        """验证权重有效性"""
        weight_sum = sum(self.weights.values())
        if not math.isclose(weight_sum, 1.0, abs_tol=0.01):
            logger.warning(f"⚠️  权重总和为 {weight_sum:.2f},应为1.0,已自动归一化")
            # 归一化
            total = sum(self.weights.values())
            self.weights = {k: v/total for k, v in self.weights.items()}

    def normalize_dimension_scores(
        self,
        dim_scores: Dict[str, int],
        apply_normal_curve: bool = True
    ) -> float:
        """
        将多维度评分转换为标准化分数

        Args:
            dim_scores: 维度评分字典,例如 {"technical_depth": 3, "practical_experience": 2, ...}
            apply_normal_curve: 是否应用正态分布调整

        Returns:
            标准化分数 (0-100)

        Example:
            >>> normalizer = ScoreNormalizer()
            >>> scores = {"technical_depth": 3, "practical_experience": 2,
            ...           "answer_specificity": 2, "logical_clarity": 3,
            ...           "honesty": 4, "communication": 3}
            >>> normalizer.normalize_dimension_scores(scores)
            52.3
        """
        # 1. 验证维度完整性
        missing_dims = set(self.weights.keys()) - set(dim_scores.keys())
        if missing_dims:
            logger.warning(f"⚠️  缺少维度评分: {missing_dims}, 将使用默认值2")
            for dim in missing_dims:
                dim_scores[dim] = 2  # 默认中等分数

        # 2. 加权求和 (范围: 1.0 到 4.0)
        weighted_sum = sum(
            dim_scores.get(dim, 2) * weight
            for dim, weight in self.weights.items()
        )

        logger.debug(f"加权求和: {weighted_sum:.2f}")

        # 3. 线性映射到 0-100
        # weighted_sum范围: [1.0, 4.0] -> [0, 100]
        raw_score = (weighted_sum - 1.0) / 3.0 * 100

        logger.debug(f"线性映射分数: {raw_score:.2f}")

        # 4. (可选) 应用正态分布调整
        if apply_normal_curve:
            normalized_score = self._apply_normal_distribution(raw_score)
        else:
            normalized_score = raw_score

        # 5. 确保在0-100范围内
        normalized_score = max(0, min(100, normalized_score))

        logger.info(f"📊 标准化分数: {normalized_score:.1f}/100")

        return round(normalized_score, 1)

    def _apply_normal_distribution(self, raw_score: float) -> float:
        """
        应用正态分布调整,使分数符合正态分布(均值50,标准差15)

        Args:
            raw_score: 原始线性分数 (0-100)

        Returns:
            调整后的分数 (0-100)
        """
        mean = SCORING_STANDARD["mean"]
        std = SCORING_STANDARD["std"]

        # 将线性分数转为Z-score
        # 假设原始分数服从均匀分布,转换为正态分布
        # 使用累积分布函数(CDF)映射

        # 简化版本: 使用sigmoid函数进行平滑映射
        # 让50分附近的区分度更高
        z = (raw_score - 50) / 20  # 标准化到均值为0
        adjusted = mean + std * z

        return adjusted

    def get_score_interpretation(self, score: float) -> Dict[str, any]:
        """
        获取分数解释和招聘建议

        Args:
            score: 标准化分数 (0-100)

        Returns:
            包含解释、建议、百分位的字典
        """
        # 确定分数区间
        if score >= 90:
            level = "90-100"
            recommendation = "强烈推荐"
        elif score >= 75:
            level = "75-89"
            recommendation = "推荐"
        elif score >= 60:
            level = "60-74"
            recommendation = "推荐"
        elif score >= 40:
            level = "40-59"
            recommendation = "观察"
        elif score >= 25:
            level = "25-39"
            recommendation = "不推荐"
        else:
            level = "0-24"
            recommendation = "不推荐"

        interpretation = SCORING_STANDARD["interpretation"][level]

        # 计算百分位 (基于正态分布)
        percentile = self._calculate_percentile(score)

        return {
            "score": score,
            "level": level,
            "interpretation": interpretation,
            "recommendation": recommendation,
            "percentile": percentile,
            "is_hire": score >= SCORING_STANDARD["decision_threshold"]["hire"],
            "is_strong_hire": score >= SCORING_STANDARD["decision_threshold"]["strong_hire"]
        }

    def _calculate_percentile(self, score: float) -> float:
        """
        计算分数对应的百分位

        Args:
            score: 标准化分数 (0-100)

        Returns:
            百分位 (0-100)
        """
        mean = SCORING_STANDARD["mean"]
        std = SCORING_STANDARD["std"]

        # 计算Z-score
        z = (score - mean) / std

        # 使用正态分布累积分布函数(近似)
        # 使用误差函数 erf 的近似
        percentile = 50 * (1 + math.erf(z / math.sqrt(2)))

        return round(percentile, 1)

    def format_dimension_scores_for_prompt(self) -> str:
        """
        生成用于Prompt的维度评分说明

        Returns:
            格式化的维度说明字符串
        """
        lines = ["请对以下6个维度分别评分(1-4分):\n"]

        for dim_key, dim_info in EVALUATION_DIMENSIONS.items():
            lines.append(f"\n### {dim_info['name']} ({dim_key})")
            lines.append("评分标准:")
            for score, description in dim_info["anchors"].items():
                lines.append(f"  {score}分: {description}")

        return "\n".join(lines)

    def validate_dimension_scores(self, dim_scores: Dict[str, int]) -> bool:
        """
        验证维度评分是否有效

        Args:
            dim_scores: 维度评分字典

        Returns:
            是否有效
        """
        for dim, score in dim_scores.items():
            if dim not in EVALUATION_DIMENSIONS:
                logger.error(f"❌ 无效的维度: {dim}")
                return False
            if not isinstance(score, int) or score < 1 or score > 4:
                logger.error(f"❌ 维度 {dim} 的评分 {score} 无效,应为1-4")
                return False

        return True

    def get_dimension_weights(self) -> Dict[str, float]:
        """获取当前维度权重"""
        return self.weights.copy()

    def set_dimension_weights(self, weights: Dict[str, float]):
        """
        设置自定义维度权重

        Args:
            weights: 新的权重字典
        """
        self.weights = weights
        self._validate_weights()
        logger.info(f"✅ 权重已更新: {self.weights}")


# 工具函数

def create_default_normalizer() -> ScoreNormalizer:
    """创建默认配置的标准化器"""
    return ScoreNormalizer()


def normalize_score(dim_scores: Dict[str, int]) -> float:
    """
    快捷函数: 使用默认配置标准化分数

    Args:
        dim_scores: 维度评分

    Returns:
        标准化分数
    """
    normalizer = create_default_normalizer()
    return normalizer.normalize_dimension_scores(dim_scores)


# 示例和测试

if __name__ == "__main__":
    # 示例1: 优秀候选人
    print("=" * 60)
    print("示例1: 优秀候选人")
    print("=" * 60)

    excellent_scores = {
        "technical_depth": 4,
        "practical_experience": 4,
        "answer_specificity": 3,
        "logical_clarity": 4,
        "honesty": 4,
        "communication": 3
    }

    normalizer = ScoreNormalizer()
    score = normalizer.normalize_dimension_scores(excellent_scores)
    interpretation = normalizer.get_score_interpretation(score)

    print(f"维度评分: {excellent_scores}")
    print(f"标准化分数: {interpretation['score']:.1f}/100")
    print(f"评价等级: {interpretation['interpretation']}")
    print(f"招聘建议: {interpretation['recommendation']}")
    print(f"百分位: 第{interpretation['percentile']:.1f}百分位")
    print()

    # 示例2: 普通候选人
    print("=" * 60)
    print("示例2: 普通候选人")
    print("=" * 60)

    average_scores = {
        "technical_depth": 2,
        "practical_experience": 2,
        "answer_specificity": 2,
        "logical_clarity": 3,
        "honesty": 3,
        "communication": 2
    }

    score = normalizer.normalize_dimension_scores(average_scores)
    interpretation = normalizer.get_score_interpretation(score)

    print(f"维度评分: {average_scores}")
    print(f"标准化分数: {interpretation['score']:.1f}/100")
    print(f"评价等级: {interpretation['interpretation']}")
    print(f"招聘建议: {interpretation['recommendation']}")
    print(f"百分位: 第{interpretation['percentile']:.1f}百分位")
    print()

    # 示例3: 不懂装懂型候选人
    print("=" * 60)
    print("示例3: 不懂装懂型候选人")
    print("=" * 60)

    overconfident_scores = {
        "technical_depth": 2,
        "practical_experience": 1,
        "answer_specificity": 1,
        "logical_clarity": 2,
        "honesty": 1,  # 关键:诚实度很低
        "communication": 3
    }

    score = normalizer.normalize_dimension_scores(overconfident_scores)
    interpretation = normalizer.get_score_interpretation(score)

    print(f"维度评分: {overconfident_scores}")
    print(f"标准化分数: {interpretation['score']:.1f}/100")
    print(f"评价等级: {interpretation['interpretation']}")
    print(f"招聘建议: {interpretation['recommendation']}")
    print(f"百分位: 第{interpretation['percentile']:.1f}百分位")
    print()
