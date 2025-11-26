"""
历史记录页面
查看历史面试记录，分析系统评估能力
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from frontend.data_loader import DataLoader
from frontend.visualizations import (
    create_score_chart,
    create_timeline_chart,
    create_comparison_chart,
    create_score_distribution_chart,
    create_dimension_comparison_chart,
    create_dimension_radar_chart,
    create_skills_bar_chart
)

# 页面配置
st.set_page_config(
    page_title="历史记录 - HRM1",
    page_icon="📊",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card h2 {
        margin: 0;
        font-size: 2.5rem;
    }
    .metric-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .interview-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .interview-card:hover {
        background: #e2e8f0;
        transform: translateX(5px);
    }
    .detail-section {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def format_duration(seconds):
    """格式化时长"""
    minutes = int(seconds / 60)
    return f"{minutes}分{int(seconds % 60)}秒"


def main():
    st.title("📊 历史记录")
    st.markdown("查看和分析历史面试数据 | 评估系统能力")
    st.markdown("---")
    
    # 加载数据
    loader = DataLoader()
    
    # 顶部统计卡片
    st.subheader("📈 系统概览")
    
    stats = loader.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{stats.get('total_interviews', 0)}</h2>
            <p>总面试次数</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h2>{stats.get('avg_score', 0):.1f}</h2>
            <p>平均推荐度</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h2>{stats.get('avg_duration', 0):.1f}</h2>
            <p>平均时长(分钟)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        max_score = stats.get('max_score', 0)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <h2>{max_score:.1f}</h2>
            <p>最高评分</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tab切换
    tab1, tab2, tab3, tab4 = st.tabs(["📋 面试列表", "📊 数据分析", "🔍 详细查看", "📥 数据导出"])
    
    # Tab 1: 面试列表
    with tab1:
        st.subheader("📋 所有面试记录")
        
        # 搜索和过滤
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_name = st.text_input("🔍 候选人姓名", "")
        
        with col2:
            search_job = st.text_input("💼 职位名称", "")
        
        with col3:
            score_range = st.slider(
                "📊 分数范围",
                min_value=0,
                max_value=100,
                value=(0, 100)
            )
        
        # 加载面试列表
        interviews = loader.search_interviews(
            candidate_name=search_name if search_name else None,
            job_title=search_job if search_job else None,
            min_score=score_range[0],
            max_score=score_range[1]
        )
        
        st.markdown(f"**找到 {len(interviews)} 条记录**")
        
        # 显示面试列表
        for interview in interviews:
            interview_id = interview.get('interview_id', '')
            candidate_name = interview.get('candidate_name', '')
            job_title = interview.get('job_title', '')
            score = interview.get('recommendation_score', 0)
            start_time = interview.get('start_time', '')
            duration = interview.get('duration_seconds', 0)
            
            # 分数颜色
            if score >= 80:
                score_color = "#10b981"
                score_label = "强烈推荐"
            elif score >= 60:
                score_color = "#3b82f6"
                score_label = "推荐"
            elif score >= 40:
                score_color = "#f59e0b"
                score_label = "观察"
            else:
                score_color = "#ef4444"
                score_label = "不推荐"
            
            # 格式化时间
            try:
                dt = datetime.fromisoformat(start_time)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = start_time
            
            # 面试卡片
            with st.expander(f"**{candidate_name}** - {job_title} | {time_str}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**面试ID:** {interview_id}")
                    st.markdown(f"**候选人:** {candidate_name}")
                    st.markdown(f"**职位:** {job_title}")
                    st.markdown(f"**时间:** {time_str}")
                    st.markdown(f"**时长:** {format_duration(duration)}")
                
                with col2:
                    st.markdown(f"**推荐度评分**")
                    st.markdown(f"<h1 style='color: {score_color}; margin: 0;'>{score:.1f}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: {score_color};'>{score_label}</p>", unsafe_allow_html=True)
                
                # 评估摘要
                evaluation = interview.get('evaluation', {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'strengths' in evaluation:
                        st.markdown("**✨ 优势:**")
                        for strength in evaluation['strengths'][:3]:
                            st.markdown(f"- {strength}")
                
                with col2:
                    if 'improvements' in evaluation:
                        st.markdown("**📈 改进建议:**")
                        for improvement in evaluation['improvements'][:3]:
                            st.markdown(f"- {improvement}")
                
                # 查看详情按钮
                if st.button(f"查看完整详情", key=f"detail_{interview_id}"):
                    st.session_state.selected_interview_id = interview_id
                    st.rerun()
    
    # Tab 2: 数据分析
    with tab2:
        st.subheader("📊 数据分析与可视化")
        
        df = loader.get_interviews_dataframe()
        
        if not df.empty:
            # 分数分布
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 评分分布")
                fig = create_score_distribution_chart(stats)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### ⏱️ 面试时间线")
                fig = create_timeline_chart(df)
                st.plotly_chart(fig, use_container_width=True)
            
            # 维度分析
            if 'dimension_averages' in stats and stats['dimension_averages']:
                st.markdown("#### 🎯 系统评估能力分析 - 平均维度评分")
                
                dimension_names = {
                    "technical_depth": "技术深度",
                    "practical_experience": "实践经验",
                    "answer_specificity": "回答具体性",
                    "logical_clarity": "逻辑清晰度",
                    "honesty": "诚实度",
                    "communication": "沟通能力"
                }
                
                # 重命名维度
                renamed_dims = {
                    dimension_names.get(k, k): v 
                    for k, v in stats['dimension_averages'].items()
                }
                
                fig = create_dimension_radar_chart(renamed_dims)
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("""
                **💡 系统评估能力解读：**
                - **技术深度**: 系统识别技术深度的准确性
                - **实践经验**: 系统评估实践经验的能力
                - **回答具体性**: 系统判断回答详细程度的能力
                - **逻辑清晰度**: 系统评估逻辑性的准确度
                - **诚实度**: 系统检测知识盲区的能力
                - **沟通能力**: 系统评估沟通表达的准确性
                
                平均分越高，说明系统在该维度的评估能力越强。
                """)
            
            # 候选人对比
            st.markdown("#### 🔄 候选人对比（最近5个）")
            recent_interviews = loader.get_recent_interviews(5)
            
            if len(recent_interviews) >= 2:
                fig = create_comparison_chart(recent_interviews)
                st.plotly_chart(fig, use_container_width=True)
                
                # 多维度对比
                fig = create_dimension_comparison_chart(recent_interviews)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("至少需要2个面试记录才能进行对比")
            
            # 趋势分析
            st.markdown("#### 📈 评分趋势")
            
            if 'start_time' in df.columns and len(df) >= 3:
                df_sorted = df.sort_values('start_time')
                
                # 计算移动平均
                df_sorted['score_ma'] = df_sorted['recommendation_score'].rolling(window=3, min_periods=1).mean()
                
                import plotly.express as px
                fig = px.line(
                    df_sorted,
                    x='start_time',
                    y=['recommendation_score', 'score_ma'],
                    title='评分趋势与移动平均',
                    labels={
                        'value': '评分',
                        'start_time': '时间',
                        'variable': '指标'
                    }
                )
                fig.update_layout(
                    height=400,
                    font={'family': "Microsoft YaHei"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("数据不足，无法显示趋势分析（需要至少3条记录）")
        
        else:
            st.info("📭 暂无面试数据")
    
    # Tab 3: 详细查看
    with tab3:
        st.subheader("🔍 面试详情")
        
        # 选择面试
        interviews = loader.load_all_interviews()
        
        if interviews:
            # 创建选择列表
            interview_options = {
                f"{i.get('candidate_name', '')} - {i.get('job_title', '')} ({i.get('interview_id', '')})": i.get('interview_id', '')
                for i in interviews
            }
            
            selected_label = st.selectbox(
                "选择面试记录",
                options=list(interview_options.keys())
            )
            
            interview_id = interview_options[selected_label]
            interview = loader.load_interview_by_id(interview_id)
            
            if interview:
                # 基本信息
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("候选人", interview.get('candidate_name', ''))
                
                with col2:
                    st.metric("职位", interview.get('job_title', ''))
                
                with col3:
                    st.metric("推荐度评分", f"{interview.get('recommendation_score', 0):.1f}/100")
                
                st.markdown("---")
                
                # 评估报告
                evaluation = interview.get('evaluation', {})
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # 综合评分
                    score = interview.get('recommendation_score', 0)
                    fig = create_score_chart(score, "综合推荐度")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # 维度雷达图
                    if 'dimension_scores_summary' in evaluation:
                        dimension_names = {
                            "technical_depth": "技术深度",
                            "practical_experience": "实践经验",
                            "answer_specificity": "回答具体性",
                            "logical_clarity": "逻辑清晰度",
                            "honesty": "诚实度",
                            "communication": "沟通能力"
                        }
                        renamed_dims = {
                            dimension_names.get(k, k): v 
                            for k, v in evaluation['dimension_scores_summary'].items()
                        }
                        fig = create_dimension_radar_chart(renamed_dims)
                        st.plotly_chart(fig, use_container_width=True)
                
                # 技能评分
                if 'skill_scores' in evaluation:
                    st.markdown("### 💪 技能评分")
                    fig = create_skills_bar_chart(evaluation['skill_scores'])
                    st.plotly_chart(fig, use_container_width=True)
                
                # 文字评估
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'strengths' in evaluation:
                        st.markdown("### ✨ 优势")
                        for strength in evaluation['strengths']:
                            st.success(f"✓ {strength}")
                
                with col2:
                    if 'improvements' in evaluation:
                        st.markdown("### 📈 改进建议")
                        for improvement in evaluation['improvements']:
                            st.warning(f"• {improvement}")
                
                # 总结
                if 'summary' in evaluation:
                    st.markdown("### 📝 总结")
                    st.info(evaluation['summary'])
                
                if 'recommendation' in evaluation:
                    st.markdown("### 🎯 招聘建议")
                    st.markdown(f"**{evaluation['recommendation']}**")
                
                st.markdown("---")
                
                # 对话记录
                st.markdown("### 💬 完整对话记录")
                
                conversation = interview.get('conversation_log', [])
                
                for i, msg in enumerate(conversation):
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    
                    if role == 'interviewer':
                        st.markdown(f"""
                        <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #3b82f6;">
                            <strong>👔 面试官:</strong><br>{content}
                        </div>
                        """, unsafe_allow_html=True)
                    elif role == 'candidate':
                        st.markdown(f"""
                        <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #10b981;">
                            <strong>👤 候选人:</strong><br>{content}
                        </div>
                        """, unsafe_allow_html=True)
                    elif role == 'system':
                        st.markdown(f"""
                        <div style="background: #fef3c7; padding: 0.5rem; border-radius: 8px; margin: 0.5rem 0;">
                            <strong>📢 系统:</strong> {content}
                        </div>
                        """, unsafe_allow_html=True)
                
                # 简历信息
                if 'resume' in interview and interview['resume']:
                    st.markdown("---")
                    st.markdown("### 📄 候选人简历")
                    
                    resume = interview['resume']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**姓名:** {resume.get('name', '')}")
                        st.markdown(f"**邮箱:** {resume.get('email', '')}")
                        st.markdown(f"**电话:** {resume.get('phone', '')}")
                    
                    with col2:
                        st.markdown(f"**教育背景:** {resume.get('education', [{}])[0].get('degree', '')} - {resume.get('education', [{}])[0].get('school', '')}")
                    
                    if 'work_experience' in resume:
                        st.markdown("**工作经验:**")
                        for exp in resume['work_experience']:
                            st.markdown(f"- **{exp.get('position', '')}** @ {exp.get('company', '')} ({exp.get('duration', '')})")
                            st.markdown(f"  {exp.get('description', '')}")
        else:
            st.info("📭 暂无面试数据")
    
    # Tab 4: 数据导出
    with tab4:
        st.subheader("📥 数据导出")
        
        st.markdown("""
        将面试数据导出为CSV格式，方便进行进一步分析或备份。
        """)
        
        df = loader.get_interviews_dataframe()
        
        if not df.empty:
            # 预览数据
            st.markdown("#### 📋 数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.markdown(f"**总记录数:** {len(df)}")
            
            # 导出按钮
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("📥 导出为CSV", use_container_width=True):
                    # 生成CSV
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    
                    # 下载按钮
                    st.download_button(
                        label="下载CSV文件",
                        data=csv,
                        file_name=f"interviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    st.success("✅ CSV文件已准备好下载")
        else:
            st.info("📭 暂无数据可导出")


if __name__ == "__main__":
    main()
