"""
随机候选人测试 - Full模式版本
生成完全随机的候选人和公司配置，在Full模式下测试面试官评估的准确度
"""

import sys
import json
import statistics
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.random_generator import RandomCandidateGenerator, RandomCompanyGenerator
from core.personality_generator import PersonalityGenerator
from core import InterviewEngine
from loguru import logger


class AccuracyAnalyzer:
    """评估准确度分析器"""
    
    def __init__(self):
        self.results = []
    
    def calculate_true_skill_score(self, skills: Dict[str, int]) -> float:
        """
        计算真实技能总分（0-100）
        
        Args:
            skills: 技能字典 {skill_name: score}
            
        Returns:
            标准化的总分 (0-100)
        """
        if not skills:
            return 0.0
        
        # 计算平均分（0-10）然后转换为0-100
        avg_score = sum(skills.values()) / len(skills)
        return avg_score * 10
    
    def add_result(
        self,
        candidate_name: str,
        level: str,
        true_skills: Dict[str, int],
        interview_score: int,
        interview_recommendation: str,
        followup_count: int,
        overconfident_detected: bool
    ):
        """添加一个测试结果"""
        true_score = self.calculate_true_skill_score(true_skills)
        
        # 计算误差
        error = abs(interview_score - true_score)
        error_rate = error / true_score * 100 if true_score > 0 else 0
        
        self.results.append({
            "name": candidate_name,
            "level": level,
            "true_score": round(true_score, 1),
            "interview_score": interview_score,
            "error": round(error, 1),
            "error_rate": round(error_rate, 1),
            "recommendation": interview_recommendation,
            "followup_count": followup_count,
            "overconfident_detected": overconfident_detected
        })
    
    def calculate_statistics(self) -> Dict:
        """计算统计指标"""
        if not self.results:
            return {}
        
        errors = [r["error"] for r in self.results]
        error_rates = [r["error_rate"] for r in self.results]
        true_scores = [r["true_score"] for r in self.results]
        interview_scores = [r["interview_score"] for r in self.results]
        
        # 计算相关系数（Pearson）
        n = len(true_scores)
        mean_true = statistics.mean(true_scores)
        mean_interview = statistics.mean(interview_scores)
        
        numerator = sum((true_scores[i] - mean_true) * (interview_scores[i] - mean_interview) 
                       for i in range(n))
        denominator_true = sum((x - mean_true) ** 2 for x in true_scores) ** 0.5
        denominator_interview = sum((x - mean_interview) ** 2 for x in interview_scores) ** 0.5
        
        correlation = 0
        if denominator_true > 0 and denominator_interview > 0:
            correlation = numerator / (denominator_true * denominator_interview)
        
        return {
            "total_tests": len(self.results),
            "mean_error": round(statistics.mean(errors), 2),
            "median_error": round(statistics.median(errors), 2),
            "std_error": round(statistics.stdev(errors), 2) if len(errors) > 1 else 0,
            "max_error": round(max(errors), 2),
            "min_error": round(min(errors), 2),
            "mean_error_rate": round(statistics.mean(error_rates), 2),
            "correlation": round(correlation, 3),
            "overconfident_detected_count": sum(1 for r in self.results if r["overconfident_detected"]),
            "total_followups": sum(r["followup_count"] for r in self.results)
        }
    
    def print_report(self):
        """打印详细报告"""
        print("\n" + "="*100)
        print("📊 随机候选人测试报告 - FULL模式评估准确度分析")
        print("="*100)
        
        # 详细结果表格
        print(f"\n{'姓名':<8} {'级别':<8} {'真实分数':<10} {'面试评分':<10} "
              f"{'误差':<8} {'误差率%':<10} {'建议':<10} {'追问':<6} {'过度自信':<8}")
        print("-" * 100)
        
        for r in self.results:
            print(f"{r['name']:<8} {r['level']:<8} {r['true_score']:<10} "
                  f"{r['interview_score']:<10} {r['error']:<8} {r['error_rate']:<10} "
                  f"{r['recommendation']:<10} {r['followup_count']:<6} "
                  f"{'是' if r['overconfident_detected'] else '否':<8}")
        
        # 统计指标
        stats = self.calculate_statistics()
        
        print("\n" + "="*100)
        print("📈 统计指标")
        print("="*100)
        
        print(f"\n总测试数: {stats['total_tests']}")
        print(f"\n评分误差:")
        print(f"  - 平均误差: {stats['mean_error']} 分")
        print(f"  - 中位误差: {stats['median_error']} 分")
        print(f"  - 标准差: {stats['std_error']} 分")
        print(f"  - 最大误差: {stats['max_error']} 分")
        print(f"  - 最小误差: {stats['min_error']} 分")
        print(f"  - 平均误差率: {stats['mean_error_rate']}%")
        
        print(f"\n相关性分析:")
        print(f"  - Pearson相关系数: {stats['correlation']}")
        
        correlation_desc = ""
        if stats['correlation'] >= 0.9:
            correlation_desc = "非常强正相关 ✅"
        elif stats['correlation'] >= 0.7:
            correlation_desc = "强正相关 ✅"
        elif stats['correlation'] >= 0.5:
            correlation_desc = "中等正相关 ⚡"
        else:
            correlation_desc = "弱相关 ⚠️"
        print(f"  - 解释: {correlation_desc}")
        
        print(f"\n追问机制:")
        print(f"  - 总追问次数: {stats['total_followups']}")
        print(f"  - 检测到过度自信: {stats['overconfident_detected_count']}人")
        
        # 准确度评级
        print("\n" + "="*100)
        print("🎯 评估系统准确度评级")
        print("="*100)
        
        accuracy_score = 0
        
        # 1. 误差评分 (40分)
        if stats['mean_error'] <= 5:
            error_score = 40
            error_grade = "优秀"
        elif stats['mean_error'] <= 10:
            error_score = 30
            error_grade = "良好"
        elif stats['mean_error'] <= 15:
            error_score = 20
            error_grade = "及格"
        else:
            error_score = 10
            error_grade = "需改进"
        
        print(f"\n1. 平均误差评分: {error_score}/40 ({error_grade})")
        print(f"   平均误差 {stats['mean_error']} 分")
        accuracy_score += error_score
        
        # 2. 相关性评分 (40分)
        if stats['correlation'] >= 0.9:
            corr_score = 40
            corr_grade = "优秀"
        elif stats['correlation'] >= 0.7:
            corr_score = 30
            corr_grade = "良好"
        elif stats['correlation'] >= 0.5:
            corr_score = 20
            corr_grade = "及格"
        else:
            corr_score = 10
            corr_grade = "需改进"
        
        print(f"\n2. 相关性评分: {corr_score}/40 ({corr_grade})")
        print(f"   相关系数 {stats['correlation']}")
        accuracy_score += corr_score
        
        # 3. 追问效果评分 (20分)
        followup_effectiveness = stats['overconfident_detected_count'] / max(stats['total_tests'] * 0.3, 1)
        if followup_effectiveness >= 0.8:
            followup_score = 20
            followup_grade = "优秀"
        elif followup_effectiveness >= 0.5:
            followup_score = 15
            followup_grade = "良好"
        elif followup_effectiveness >= 0.3:
            followup_score = 10
            followup_grade = "及格"
        else:
            followup_score = 5
            followup_grade = "需改进"
        
        print(f"\n3. 追问机制评分: {followup_score}/20 ({followup_grade})")
        print(f"   检测过度自信率 {stats['overconfident_detected_count']}/{stats['total_tests']}")
        accuracy_score += followup_score
        
        print(f"\n{'='*100}")
        print(f"总分: {accuracy_score}/100")
        print(f"{'='*100}")
        
        if accuracy_score >= 85:
            print("\n🎉 系统评估准确度：优秀！")
        elif accuracy_score >= 70:
            print("\n✅ 系统评估准确度：良好")
        elif accuracy_score >= 60:
            print("\n⚡ 系统评估准确度：及格")
        else:
            print("\n⚠️  系统评估准确度：需要改进")
        
        return stats


def run_random_test_full_mode(num_candidates: int = 10, seed: int = None):
    """
    运行随机候选人测试 - FULL模式
    
    Args:
        num_candidates: 测试候选人数量
        seed: 随机种子
    """
    print("\n" + "="*100)
    print(f"🎲 随机候选人测试 FULL模式 - 测试{num_candidates}个候选人")
    print("="*100)
    
    # 初始化生成器
    candidate_gen = RandomCandidateGenerator(seed=seed)
    company_gen = RandomCompanyGenerator(seed=seed)
    personality_gen = PersonalityGenerator(seed=seed)
    
    # 初始化分析器
    analyzer = AccuracyAnalyzer()
    
    # 生成随机公司（所有候选人用同一家公司）
    company_config = company_gen.generate_company()
    job_config = company_gen.generate_job()
    
    print(f"\n🏢 公司: {company_config['name']} ({company_config['type']})")
    print(f"💼 职位: {job_config['title']}")
    print(f"📋 要求技能: {', '.join(job_config['required_skills'][:5])}...")
    
    # 临时保存公司和职位配置
    temp_company_file = Path("config/companies/_temp_random_company.json")
    temp_job_file = Path("config/jobs/_temp_random_job.json")
    
    temp_company_file.parent.mkdir(parents=True, exist_ok=True)
    temp_job_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(temp_company_file, 'w', encoding='utf-8') as f:
        json.dump(company_config, f, ensure_ascii=False, indent=2)
    
    with open(temp_job_file, 'w', encoding='utf-8') as f:
        json.dump(job_config, f, ensure_ascii=False, indent=2)
    
    # 创建面试引擎
    engine = InterviewEngine()
    
    # 测试每个候选人
    for i in range(num_candidates):
        print(f"\n{'='*100}")
        print(f"测试 {i+1}/{num_candidates}")
        print(f"{'='*100}")
        
        # 生成随机级别
        level = ["junior", "mid", "senior"][i % 3]  # 循环使用三个级别
        
        # 生成随机性格
        personality = personality_gen.generate_random("normal").to_dict()
        
        # 生成完整候选人
        candidate_config = candidate_gen.generate_complete_candidate(
            level=level,
            personality=personality
        )
        
        candidate_name = candidate_config['profile']['name']
        true_skills = candidate_config['profile']['skills']
        
        print(f"\n👤 候选人: {candidate_name}")
        print(f"   级别: {level}")
        print(f"   技能数: {len(true_skills)}")
        print(f"   平均技能分: {sum(true_skills.values()) / len(true_skills):.1f}/10")
        print(f"   自知之明: {personality['self_perception']['self_awareness']}/100")
        
        try:
            # 执行面试 - 使用FULL模式
            result = engine.run_interview(
                job_file="_temp_random_job",
                company_file="_temp_random_company",
                candidate_config=candidate_config,
                mode="full"  # 使用FULL模式
            )
            
            # 统计追问次数
            followup_count = sum(1 for entry in result.conversation_log 
                                if isinstance(entry, dict) and entry.get('type') == 'followup')
            
            # 添加结果到分析器
            analyzer.add_result(
                candidate_name=candidate_name,
                level=level,
                true_skills=true_skills,
                interview_score=result.recommendation_score,
                interview_recommendation=result.evaluation.get('recommendation', 'N/A'),
                followup_count=followup_count,
                overconfident_detected=result.evaluation.get('overconfidence_detected', False)
            )
            
            print(f"\n✅ 面试完成")
            print(f"   推荐度: {result.recommendation_score}/100")
            print(f"   建议: {result.evaluation.get('recommendation', 'N/A')}")
            print(f"   追问: {followup_count}次")
            
        except Exception as e:
            logger.error(f"❌ 面试失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 清理临时文件
    temp_company_file.unlink(missing_ok=True)
    temp_job_file.unlink(missing_ok=True)
    
    # 生成报告
    stats = analyzer.print_report()
    
    # 保存详细结果
    output_file = Path("data/analysis/random_test_full_mode_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "mode": "full",
            "config": {
                "num_candidates": num_candidates,
                "seed": seed,
                "company": company_config['name'],
                "job": job_config['title']
            },
            "results": analyzer.results,
            "statistics": stats
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细结果已保存至: {output_file}")
    
    return analyzer, stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="随机候选人测试 - Full模式")
    parser.add_argument("--num", type=int, default=10, help="测试候选人数量")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    
    args = parser.parse_args()
    
    try:
        analyzer, stats = run_random_test_full_mode(
            num_candidates=args.num,
            seed=args.seed
        )
        
        print("\n" + "="*100)
        print("🎉 Full模式随机测试完成！")
        print("="*100)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
