"""
数据加载器
负责加载和解析历史面试记录、简历、评估报告等数据
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd


class DataLoader:
    """数据加载器类"""
    
    def __init__(self, data_root: str = "data"):
        self.data_root = Path(data_root)
        self.interviews_dir = self.data_root / "interviews"
        self.analysis_dir = self.data_root / "analysis"
        self.resumes_dir = self.data_root / "resumes"
        
    def load_all_interviews(self) -> List[Dict]:
        """
        加载所有历史面试记录
        
        Returns:
            面试记录列表
        """
        interviews = []
        
        if not self.interviews_dir.exists():
            return interviews
        
        for json_file in sorted(self.interviews_dir.glob("*.json"), reverse=True):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['file_path'] = str(json_file)
                    interviews.append(data)
            except Exception as e:
                print(f"加载 {json_file} 失败: {e}")
        
        return interviews
    
    def load_interview_by_id(self, interview_id: str) -> Optional[Dict]:
        """
        根据ID加载特定面试记录
        
        Args:
            interview_id: 面试ID
            
        Returns:
            面试记录字典，如果未找到则返回None
        """
        for json_file in self.interviews_dir.glob("*.json"):
            if interview_id in json_file.name:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"加载面试记录失败: {e}")
                    return None
        return None
    
    def get_interviews_dataframe(self) -> pd.DataFrame:
        """
        将面试记录转换为DataFrame用于分析
        
        Returns:
            面试记录DataFrame
        """
        interviews = self.load_all_interviews()
        
        if not interviews:
            return pd.DataFrame()
        
        records = []
        for interview in interviews:
            record = {
                'interview_id': interview.get('interview_id', ''),
                'candidate_name': interview.get('candidate_name', ''),
                'job_title': interview.get('job_title', ''),
                'start_time': interview.get('start_time', ''),
                'recommendation_score': interview.get('recommendation_score', 0),
                'duration_seconds': interview.get('duration_seconds', 0),
            }
            
            # 提取维度评分
            evaluation = interview.get('evaluation', {})
            dimension_scores = evaluation.get('dimension_scores_summary', {})
            for dim, score in dimension_scores.items():
                record[f'dim_{dim}'] = score
            
            # 提取总体建议
            record['recommendation'] = evaluation.get('recommendation', '')
            
            records.append(record)
        
        df = pd.DataFrame(records)
        
        # 转换时间
        if 'start_time' in df.columns and not df.empty:
            df['start_time'] = pd.to_datetime(df['start_time'])
        
        return df
    
    def get_statistics(self) -> Dict:
        """
        获取面试系统的统计数据
        
        Returns:
            统计数据字典
        """
        df = self.get_interviews_dataframe()
        
        if df.empty:
            return {
                'total_interviews': 0,
                'avg_score': 0,
                'avg_duration': 0,
                'score_distribution': {}
            }
        
        stats = {
            'total_interviews': len(df),
            'avg_score': df['recommendation_score'].mean() if 'recommendation_score' in df.columns else 0,
            'avg_duration': df['duration_seconds'].mean() / 60 if 'duration_seconds' in df.columns else 0,  # 转换为分钟
            'max_score': df['recommendation_score'].max() if 'recommendation_score' in df.columns else 0,
            'min_score': df['recommendation_score'].min() if 'recommendation_score' in df.columns else 0,
        }
        
        # 分数分布
        if 'recommendation_score' in df.columns:
            score_bins = [0, 40, 60, 80, 100]
            score_labels = ['不推荐', '观察', '推荐', '强烈推荐']
            df['score_category'] = pd.cut(
                df['recommendation_score'],
                bins=score_bins,
                labels=score_labels,
                include_lowest=True
            )
            stats['score_distribution'] = df['score_category'].value_counts().to_dict()
        
        # 维度评分平均
        dimension_cols = [col for col in df.columns if col.startswith('dim_')]
        if dimension_cols:
            stats['dimension_averages'] = {
                col.replace('dim_', ''): df[col].mean()
                for col in dimension_cols
            }
        
        return stats
    
    def search_interviews(
        self,
        candidate_name: Optional[str] = None,
        job_title: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        搜索面试记录
        
        Args:
            candidate_name: 候选人姓名（支持模糊搜索）
            job_title: 职位名称（支持模糊搜索）
            min_score: 最低分数
            max_score: 最高分数
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            符合条件的面试记录列表
        """
        interviews = self.load_all_interviews()
        results = []
        
        for interview in interviews:
            # 候选人姓名过滤
            if candidate_name and candidate_name.lower() not in interview.get('candidate_name', '').lower():
                continue
            
            # 职位名称过滤
            if job_title and job_title.lower() not in interview.get('job_title', '').lower():
                continue
            
            # 分数过滤
            score = interview.get('recommendation_score', 0)
            if min_score is not None and score < min_score:
                continue
            if max_score is not None and score > max_score:
                continue
            
            # 日期过滤
            if start_date or end_date:
                interview_time = datetime.fromisoformat(interview.get('start_time', ''))
                if start_date and interview_time < start_date:
                    continue
                if end_date and interview_time > end_date:
                    continue
            
            results.append(interview)
        
        return results
    
    def load_candidate_templates(self) -> List[str]:
        """加载所有候选人模板名称"""
        templates_dir = Path("config/candidate_templates")
        if not templates_dir.exists():
            return []
        return [f.stem for f in templates_dir.glob("*.json")]
    
    def load_domains(self) -> List[str]:
        """加载所有可用的领域"""
        domains_dir = Path("domains")
        if not domains_dir.exists():
            return ["tech"]
        
        domains = []
        for domain_dir in domains_dir.iterdir():
            if domain_dir.is_dir() and (domain_dir / "domain_config.json").exists():
                domains.append(domain_dir.name)
        
        return domains if domains else ["tech"]
    
    def export_to_csv(self, output_path: str):
        """
        导出面试数据到CSV
        
        Args:
            output_path: 输出文件路径
        """
        df = self.get_interviews_dataframe()
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
    def get_recent_interviews(self, limit: int = 10) -> List[Dict]:
        """
        获取最近的面试记录
        
        Args:
            limit: 返回数量限制
            
        Returns:
            最近的面试记录列表
        """
        interviews = self.load_all_interviews()
        return interviews[:limit]
