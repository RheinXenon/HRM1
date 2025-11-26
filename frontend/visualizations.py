"""
可视化工具
提供各种图表生成功能
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import pandas as pd


def create_score_chart(score: float, title: str = "综合评分") -> go.Figure:
    """
    创建评分仪表盘
    
    Args:
        score: 分数 (0-100)
        title: 图表标题
        
    Returns:
        Plotly图表对象
    """
    # 确定颜色
    if score >= 80:
        color = "#10b981"  # 绿色
    elif score >= 60:
        color = "#f59e0b"  # 橙色
    else:
        color = "#ef4444"  # 红色
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': 60, 'increasing': {'color': "#10b981"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#fee2e2'},
                {'range': [40, 60], 'color': '#fef3c7'},
                {'range': [60, 80], 'color': '#d1fae5'},
                {'range': [80, 100], 'color': '#a7f3d0'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="white",
        font={'family': "Microsoft YaHei"}
    )
    
    return fig


def create_dimension_radar_chart(dimension_scores: Dict[str, float]) -> go.Figure:
    """
    创建维度评分雷达图
    
    Args:
        dimension_scores: 维度评分字典
        
    Returns:
        Plotly图表对象
    """
    # 维度名称映射
    dimension_names = {
        "technical_depth": "技术深度",
        "practical_experience": "实践经验",
        "answer_specificity": "回答具体性",
        "logical_clarity": "逻辑清晰度",
        "honesty": "诚实度",
        "communication": "沟通能力"
    }
    
    categories = [dimension_names.get(k, k) for k in dimension_scores.keys()]
    values = list(dimension_scores.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='候选人评分',
        line_color='#3b82f6',
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4]
            )
        ),
        showlegend=False,
        title="多维度能力雷达图",
        height=400,
        font={'family': "Microsoft YaHei"}
    )
    
    return fig


def create_timeline_chart(interviews_df: pd.DataFrame) -> go.Figure:
    """
    创建面试时间线图
    
    Args:
        interviews_df: 面试数据DataFrame
        
    Returns:
        Plotly图表对象
    """
    if interviews_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="暂无数据",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    df = interviews_df.copy()
    
    # 确保时间列存在
    if 'start_time' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="数据格式错误", x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = px.scatter(
        df,
        x='start_time',
        y='recommendation_score',
        color='recommendation_score',
        size='duration_seconds',
        hover_data=['candidate_name', 'job_title'],
        title='面试历史时间线',
        labels={
            'start_time': '面试时间',
            'recommendation_score': '推荐度评分',
            'duration_seconds': '时长(秒)'
        },
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="面试时间",
        yaxis_title="推荐度评分",
        font={'family': "Microsoft YaHei"}
    )
    
    return fig


def create_comparison_chart(interviews: List[Dict]) -> go.Figure:
    """
    创建多个面试的对比图
    
    Args:
        interviews: 面试记录列表
        
    Returns:
        Plotly图表对象
    """
    if not interviews:
        fig = go.Figure()
        fig.add_annotation(text="暂无数据", x=0.5, y=0.5, showarrow=False)
        return fig
    
    candidates = [i.get('candidate_name', 'Unknown') for i in interviews]
    scores = [i.get('recommendation_score', 0) for i in interviews]
    
    # 颜色映射
    colors = ['#10b981' if s >= 80 else '#f59e0b' if s >= 60 else '#ef4444' for s in scores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=candidates,
            y=scores,
            marker_color=colors,
            text=scores,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="候选人推荐度对比",
        xaxis_title="候选人",
        yaxis_title="推荐度评分",
        yaxis=dict(range=[0, 100]),
        height=400,
        font={'family': "Microsoft YaHei"}
    )
    
    return fig


def create_score_distribution_chart(stats: Dict) -> go.Figure:
    """
    创建分数分布饼图
    
    Args:
        stats: 统计数据字典
        
    Returns:
        Plotly图表对象
    """
    distribution = stats.get('score_distribution', {})
    
    if not distribution:
        fig = go.Figure()
        fig.add_annotation(text="暂无数据", x=0.5, y=0.5, showarrow=False)
        return fig
    
    labels = list(distribution.keys())
    values = list(distribution.values())
    
    colors = {
        '不推荐': '#ef4444',
        '观察': '#f59e0b',
        '推荐': '#3b82f6',
        '强烈推荐': '#10b981'
    }
    
    color_list = [colors.get(str(label), '#888888') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=color_list),
        hole=0.3
    )])
    
    fig.update_layout(
        title="面试结果分布",
        height=350,
        font={'family': "Microsoft YaHei"}
    )
    
    return fig


def create_dimension_comparison_chart(interviews: List[Dict]) -> go.Figure:
    """
    创建多个候选人的维度对比图
    
    Args:
        interviews: 面试记录列表
        
    Returns:
        Plotly图表对象
    """
    if not interviews:
        fig = go.Figure()
        fig.add_annotation(text="暂无数据", x=0.5, y=0.5, showarrow=False)
        return fig
    
    dimension_names = {
        "technical_depth": "技术深度",
        "practical_experience": "实践经验",
        "answer_specificity": "回答具体性",
        "logical_clarity": "逻辑清晰度",
        "honesty": "诚实度",
        "communication": "沟通能力"
    }
    
    fig = go.Figure()
    
    for interview in interviews[:5]:  # 最多对比5个候选人
        candidate_name = interview.get('candidate_name', 'Unknown')
        evaluation = interview.get('evaluation', {})
        dimension_scores = evaluation.get('dimension_scores_summary', {})
        
        if dimension_scores:
            categories = [dimension_names.get(k, k) for k in dimension_scores.keys()]
            values = list(dimension_scores.values())
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=candidate_name
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4]
            )
        ),
        title="候选人多维度能力对比",
        height=500,
        font={'family': "Microsoft YaHei"}
    )
    
    return fig


def create_skills_bar_chart(skill_scores: Dict[str, float]) -> go.Figure:
    """
    创建技能评分柱状图
    
    Args:
        skill_scores: 技能评分字典
        
    Returns:
        Plotly图表对象
    """
    if not skill_scores:
        fig = go.Figure()
        fig.add_annotation(text="暂无技能评分数据", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # 按分数排序
    sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
    skills = [s[0] for s in sorted_skills[:10]]  # 显示前10个
    scores = [s[1] for s in sorted_skills[:10]]
    
    # 颜色映射
    colors = ['#10b981' if s >= 80 else '#f59e0b' if s >= 60 else '#ef4444' for s in scores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=skills,
            y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="技能评分分布（Top 10）",
        xaxis_title="技能",
        yaxis_title="标准化评分",
        yaxis=dict(range=[0, 100]),
        height=400,
        font={'family': "Microsoft YaHei"}
    )
    
    return fig
