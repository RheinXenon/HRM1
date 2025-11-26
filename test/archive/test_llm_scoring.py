"""
真实LLM评分测试脚本
测试LLM在实际面试场景中的评分是否正常
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.llm_client import LLMClient
from core.score_normalizer import ScoreNormalizer, EVALUATION_DIMENSIONS
from agents.prompts.interviewer_prompts import ANSWER_EVALUATION_PROMPT
from loguru import logger


class LLMScoringTester:
    """LLM评分测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.llm_client = LLMClient()
        self.normalizer = ScoreNormalizer()
        
    def evaluate_answer_with_llm(
        self,
        question: str,
        answer: str,
        target_skills: List[str]
    ) -> Dict[str, Any]:
        """
        使用LLM评估回答
        
        Args:
            question: 问题
            answer: 候选人回答
            target_skills: 目标技能
            
        Returns:
            评估结果，包含多维度评分
        """
        # 构建评估提示词
        evaluation_prompt = ANSWER_EVALUATION_PROMPT.format(
            question=question,
            answer=answer,
            target_skills=", ".join(target_skills)
        )
        
        # 调用LLM进行评估
        try:
            result = self.llm_client.chat_with_json_response(
                messages=[
                    {"role": "system", "content": "你是一位专业的技术面试官，负责评估候选人的回答质量。"},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM评估失败: {e}")
            return {
                "error": str(e),
                "dimension_scores": {
                    "technical_depth": 2,
                    "practical_experience": 2,
                    "answer_specificity": 2,
                    "logical_clarity": 2,
                    "honesty": 2,
                    "communication": 2
                }
            }
    
    def test_excellent_candidate(self) -> Dict[str, Any]:
        """测试优秀候选人场景"""
        print("\n" + "="*60)
        print("🧪 测试场景1: 优秀候选人")
        print("="*60)
        
        question = "请详细解释一下Python中的装饰器(decorator)是什么，以及它在实际项目中的应用场景。"
        
        # 优秀回答：技术深度好，实践经验丰富，回答具体
        answer = """
装饰器是Python中一种非常强大的设计模式，本质上是一个接受函数作为参数并返回新函数的高阶函数。
它利用了Python的闭包特性，可以在不修改原函数代码的情况下，为函数添加额外功能。

从技术原理来说，装饰器使用@语法糖，实际上是函数调用的语法糖。例如：
@decorator
def func():
    pass
等价于 func = decorator(func)

在我之前的项目中，我大量使用了装饰器：
1. 日志记录：我写了一个@log_function装饰器，自动记录函数的输入参数、执行时间和返回值
2. 权限验证：在Web API中使用@require_auth装饰器，统一处理用户认证逻辑
3. 缓存优化：实现了@cache装饰器，对频繁调用的数据库查询结果进行缓存，显著提升了性能

特别值得一提的是，我还实现过带参数的装饰器，比如@retry(max_attempts=3)，
这需要多层嵌套函数。这种模式在处理不稳定的外部API调用时非常有用。

装饰器的优势在于代码复用和关注点分离，但也要注意过度使用会影响代码可读性。
        """
        
        target_skills = ["Python", "设计模式", "代码优化"]
        
        print(f"\n📝 问题: {question}")
        print(f"\n💬 回答: {answer[:100]}...")
        print(f"\n🎯 目标技能: {', '.join(target_skills)}")
        
        # LLM评估
        print("\n⏳ 正在调用LLM进行评估...")
        evaluation = self.evaluate_answer_with_llm(question, answer, target_skills)
        
        return self._process_evaluation_result(evaluation, "优秀候选人", expected_range=(75, 100))
    
    def test_average_candidate(self) -> Dict[str, Any]:
        """测试普通候选人场景"""
        print("\n" + "="*60)
        print("🧪 测试场景2: 普通候选人")
        print("="*60)
        
        question = "请说说你对RESTful API的理解和实践经验。"
        
        # 普通回答：基本概念正确，但缺乏深度和实践细节
        answer = """
RESTful API是一种网络应用程序的架构风格，主要用于Web服务。
它有几个特点：
1. 使用HTTP方法，比如GET用来获取数据，POST用来创建数据
2. 资源用URL表示
3. 无状态的通信

我在项目中用过RESTful API，就是写一些接口给前端调用。
比如用Flask写过一些GET和POST接口，返回JSON数据。
基本上按照这个规范来做就可以了。
        """
        
        target_skills = ["RESTful API", "Web开发", "后端架构"]
        
        print(f"\n📝 问题: {question}")
        print(f"\n💬 回答: {answer[:100]}...")
        print(f"\n🎯 目标技能: {', '.join(target_skills)}")
        
        # LLM评估
        print("\n⏳ 正在调用LLM进行评估...")
        evaluation = self.evaluate_answer_with_llm(question, answer, target_skills)
        
        return self._process_evaluation_result(evaluation, "普通候选人", expected_range=(40, 65))
    
    def test_pretentious_candidate(self) -> Dict[str, Any]:
        """测试不懂装懂候选人场景"""
        print("\n" + "="*60)
        print("🧪 测试场景3: 不懂装懂候选人")
        print("="*60)
        
        question = "请解释一下什么是分布式事务，以及你是如何在项目中解决分布式事务问题的？"
        
        # 不懂装懂回答：使用大量术语但缺乏实质内容，逻辑不清晰，细节模糊
        answer = """
分布式事务嘛，就是在分布式系统中的事务处理，这个我很熟悉。
主要就是用那个什么...两阶段提交，还有三阶段提交，
然后还有一些消息队列的方案，比如Kafka之类的。

我们项目中用了微服务架构，所以肯定会遇到分布式事务的问题。
我们用的是比较先进的方案，具体的话...就是通过一些中间件来实现的，
效果还不错，基本上没什么问题。

这个技术比较复杂，需要考虑很多东西，像CAP理论、最终一致性什么的，
我们都有考虑。总之就是要保证数据的一致性嘛。
        """
        
        target_skills = ["分布式系统", "事务处理", "微服务架构"]
        
        print(f"\n📝 问题: {question}")
        print(f"\n💬 回答: {answer[:100]}...")
        print(f"\n🎯 目标技能: {', '.join(target_skills)}")
        
        # LLM评估
        print("\n⏳ 正在调用LLM进行评估...")
        evaluation = self.evaluate_answer_with_llm(question, answer, target_skills)
        
        return self._process_evaluation_result(evaluation, "不懂装懂候选人", expected_range=(0, 45))
    
    def test_mixed_performance_candidate(self) -> Dict[str, Any]:
        """测试表现参差不齐的候选人"""
        print("\n" + "="*60)
        print("🧪 测试场景4: 表现参差不齐的候选人")
        print("="*60)
        
        question = "请介绍一下数据库索引的原理和使用场景。"
        
        # 混合回答：技术理解尚可，但实践经验不足，表达不够清晰
        answer = """
数据库索引就像书的目录一样，可以快速找到数据。
主要原理是通过B+树这种数据结构来实现的，能够减少磁盘IO次数。

索引的好处是能提高查询速度，但是也有缺点，就是会占用额外的存储空间，
而且在插入和更新数据时会变慢，因为要维护索引。

我在做项目的时候，会在一些经常查询的字段上建索引，
比如用户ID、订单号这些。但是也不能建太多索引，要权衡一下。

还有联合索引，就是多个字段一起建索引，这个我了解但实际用得不多。
        """
        
        target_skills = ["数据库", "性能优化", "索引设计"]
        
        print(f"\n📝 问题: {question}")
        print(f"\n💬 回答: {answer[:100]}...")
        print(f"\n🎯 目标技能: {', '.join(target_skills)}")
        
        # LLM评估
        print("\n⏳ 正在调用LLM进行评估...")
        evaluation = self.evaluate_answer_with_llm(question, answer, target_skills)
        
        return self._process_evaluation_result(evaluation, "参差不齐候选人", expected_range=(50, 70))
    
    def _process_evaluation_result(
        self,
        evaluation: Dict[str, Any],
        candidate_type: str,
        expected_range: tuple
    ) -> Dict[str, Any]:
        """
        处理评估结果
        
        Args:
            evaluation: LLM评估结果
            candidate_type: 候选人类型
            expected_range: 预期分数范围
            
        Returns:
            处理后的结果
        """
        print("\n📊 LLM评估结果:")
        
        # 提取维度评分
        dimension_scores = evaluation.get("dimension_scores", {})
        
        # 显示维度评分
        print("\n维度评分 (1-4分):")
        for dim_key, score in dimension_scores.items():
            dim_name = EVALUATION_DIMENSIONS.get(dim_key, {}).get("name", dim_key)
            print(f"  {dim_name}: {score}/4")
        
        # 计算标准化分数
        normalized_score = self.normalizer.normalize_dimension_scores(dimension_scores)
        interpretation = self.normalizer.get_score_interpretation(normalized_score)
        
        print(f"\n标准化分数: {normalized_score:.1f}/100")
        print(f"评价等级: {interpretation['interpretation']}")
        print(f"招聘建议: {interpretation['recommendation']}")
        print(f"百分位: 第{interpretation['percentile']:.1f}百分位")
        
        # 显示LLM的其他评估信息
        if "reasoning" in evaluation:
            print(f"\n评估理由: {evaluation['reasoning']}")
        
        if "confidence_level" in evaluation:
            print(f"可信度: {evaluation['confidence_level']}")
        
        # 验证分数范围
        expected_min, expected_max = expected_range
        in_range = expected_min <= normalized_score <= expected_max
        
        if in_range:
            print(f"\n✅ 通过: 标准化分数在预期范围 [{expected_min}, {expected_max}]")
            status = "PASS"
        else:
            print(f"\n⚠️  警告: 标准化分数 {normalized_score:.1f} 不在预期范围 [{expected_min}, {expected_max}]")
            print(f"   这可能表明LLM评分偏差或测试用例需要调整")
            status = "WARNING"
        
        return {
            "candidate_type": candidate_type,
            "dimension_scores": dimension_scores,
            "normalized_score": normalized_score,
            "interpretation": interpretation,
            "evaluation": evaluation,
            "expected_range": expected_range,
            "in_range": in_range,
            "status": status
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("\n" + "="*80)
        print("🚀 LLM评分测试套件")
        print("="*80)
        print("本测试使用真实LLM调用来评估不同类型候选人的回答")
        print("目的：验证LLM评分的合理性和一致性")
        print("="*80)
        
        results = []
        
        # 测试1: 优秀候选人
        try:
            result1 = self.test_excellent_candidate()
            results.append(result1)
        except Exception as e:
            logger.error(f"❌ 优秀候选人测试失败: {e}")
            results.append({"status": "ERROR", "candidate_type": "优秀候选人", "error": str(e)})
        
        # 测试2: 普通候选人
        try:
            result2 = self.test_average_candidate()
            results.append(result2)
        except Exception as e:
            logger.error(f"❌ 普通候选人测试失败: {e}")
            results.append({"status": "ERROR", "candidate_type": "普通候选人", "error": str(e)})
        
        # 测试3: 不懂装懂候选人
        try:
            result3 = self.test_pretentious_candidate()
            results.append(result3)
        except Exception as e:
            logger.error(f"❌ 不懂装懂候选人测试失败: {e}")
            results.append({"status": "ERROR", "candidate_type": "不懂装懂候选人", "error": str(e)})
        
        # 测试4: 参差不齐候选人
        try:
            result4 = self.test_mixed_performance_candidate()
            results.append(result4)
        except Exception as e:
            logger.error(f"❌ 参差不齐候选人测试失败: {e}")
            results.append({"status": "ERROR", "candidate_type": "参差不齐候选人", "error": str(e)})
        
        # 总结
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results: List[Dict[str, Any]]):
        """打印测试摘要"""
        print("\n" + "="*80)
        print("📊 测试摘要")
        print("="*80)
        
        print("\n候选人类型 | 标准化分数 | 预期范围 | 状态")
        print("-" * 60)
        
        pass_count = 0
        warning_count = 0
        error_count = 0
        
        for result in results:
            candidate_type = result.get("candidate_type", "未知")
            status = result.get("status", "UNKNOWN")
            
            if status == "ERROR":
                error_count += 1
                print(f"{candidate_type:15} | ERROR | - | ❌ 错误")
                if "error" in result:
                    print(f"  错误信息: {result['error']}")
            else:
                score = result.get("normalized_score", 0)
                expected = result.get("expected_range", (0, 0))
                in_range = result.get("in_range", False)
                
                status_icon = "✅" if status == "PASS" else "⚠️"
                status_text = "通过" if status == "PASS" else "警告"
                
                print(f"{candidate_type:15} | {score:6.1f} | [{expected[0]:3}, {expected[1]:3}] | {status_icon} {status_text}")
                
                if status == "PASS":
                    pass_count += 1
                else:
                    warning_count += 1
        
        # 统计
        print("\n" + "="*80)
        print(f"总计: {len(results)} 个测试")
        print(f"✅ 通过: {pass_count}")
        print(f"⚠️  警告: {warning_count}")
        print(f"❌ 错误: {error_count}")
        
        # 评估标准差
        if len(results) >= 3:
            scores = [r.get("normalized_score", 0) for r in results if "normalized_score" in r]
            if scores:
                import statistics
                mean_score = statistics.mean(scores)
                std_score = statistics.stdev(scores) if len(scores) > 1 else 0
                
                print(f"\n评分统计:")
                print(f"平均分: {mean_score:.1f}")
                print(f"标准差: {std_score:.1f}")
                
                if std_score < 10:
                    print("⚠️  警告: 评分区分度可能不足 (标准差过小)")
                elif std_score > 30:
                    print("⚠️  警告: 评分波动可能过大 (标准差过大)")
        
        print("="*80)
        
        # 最终结论
        if error_count == 0 and warning_count == 0:
            print("\n🎉 所有测试通过! LLM评分系统工作正常")
        elif error_count == 0:
            print(f"\n⚠️  存在 {warning_count} 个警告，请检查LLM评分是否需要调整")
        else:
            print(f"\n❌ 存在 {error_count} 个错误，请检查系统配置")


def main():
    """主测试函数"""
    tester = LLMScoringTester()
    results = tester.run_all_tests()
    
    # 保存结果
    output_file = Path("data/test_results/llm_scoring_test_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 简化results以便JSON序列化
    simplified_results = []
    for r in results:
        simplified = {
            "candidate_type": r.get("candidate_type"),
            "status": r.get("status"),
            "normalized_score": r.get("normalized_score"),
            "expected_range": r.get("expected_range"),
            "in_range": r.get("in_range")
        }
        if "error" in r:
            simplified["error"] = r["error"]
        simplified_results.append(simplified)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simplified_results, f, ensure_ascii=False, indent=2)
    
    logger.success(f"✅ 测试结果已保存至: {output_file}")
    
    # 返回状态码
    error_count = sum(1 for r in results if r.get("status") == "ERROR")
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
