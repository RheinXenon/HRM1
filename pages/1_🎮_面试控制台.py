"""
面试控制台页面
实时模拟面试流程，支持批量模拟、流式输出、过程控制
"""

import streamlit as st
from pathlib import Path
import sys
import time
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from frontend.interview_controller import InterviewController
from frontend.data_loader import DataLoader
from frontend.visualizations import create_score_chart, create_dimension_radar_chart, create_skills_bar_chart
from config import load_candidate_template, generate_domain_config
from core.personality_generator import PersonalityGenerator
from core.random_generator import RandomCandidateGenerator
from dataclasses import asdict
from domains import list_available_domains

# 页面配置
st.set_page_config(
    page_title="面试控制台 - HRM1",
    page_icon="🎮",
    layout="wide"
)

# 缓存领域列表加载
@st.cache_data
def get_cached_domains():
    """缓存的领域列表加载"""
    return list_available_domains()

# 初始化session_state
if 'controller' not in st.session_state:
    st.session_state.controller = InterviewController()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'interview_running' not in st.session_state:
    st.session_state.interview_running = False
if 'final_report' not in st.session_state:
    st.session_state.final_report = None
if 'candidate_info' not in st.session_state:
    st.session_state.candidate_info = None
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'interview_info' not in st.session_state:
    st.session_state.interview_info = None

# 自定义CSS
st.markdown("""
<style>
    .message-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .interviewer-msg {
        background: #eff6ff;
        border-left-color: #3b82f6;
    }
    .candidate-msg {
        background: #f0fdf4;
        border-left-color: #10b981;
    }
    .system-msg {
        background: #fef3c7;
        border-left-color: #f59e0b;
    }
    .eval-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        margin: 0.5rem 0;
    }
    .control-button {
        margin: 0.2rem;
    }
    .candidate-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .resume-section {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def generate_candidate_config(candidate_type, template_name, domain_id, strategy, archetype):
    """生成候选人配置"""
    if candidate_type == "模板候选人":
        return load_candidate_template(template_name)
    else:
        # 生成随机候选人
        generator = PersonalityGenerator()
        if archetype != "random":
            personality_config = generator.generate_archetype(archetype)
        else:
            personality_config = generator.generate_random(strategy=strategy)
        
        personality = asdict(personality_config)
        skill_generator = RandomCandidateGenerator(domain_id=domain_id)
        candidate_config = skill_generator.generate_complete_candidate(
            level="mid",
            personality=personality
        )
        return candidate_config


def main():
    st.title("🎮 面试控制台")
    st.markdown("实时模拟面试流程 | 批量测试 | 智能追问")
    st.markdown("---")
    
    # 侧边栏 - 配置区
    with st.sidebar:
        st.header("⚙️ 面试配置")
        
        # 加载可用数据
        loader = DataLoader()
        domains = loader.load_domains()
        templates = loader.load_candidate_templates()
        
        # 领域选择
        domain_id = st.selectbox(
            "🏢 选择面试领域",
            options=domains,
            format_func=lambda x: {
                'tech': '💻 技术领域',
                'marketing': '📢 营销领域',
                'healthcare': '🏥 医疗领域'
            }.get(x, x)
        )
        
        # 显示领域信息
        try:
            from domains import get_domain_info
            domain_info = get_domain_info(domain_id)
            if domain_info:
                st.info(f"**{domain_info.get('domain_name', domain_id)}**\n\n{domain_info.get('description', '')}")
        except:
            pass
        
        st.markdown("---")
        
        # 面试模式
        mode = st.radio(
            "📋 面试模式",
            options=["demo", "full"],
            format_func=lambda x: "Demo模式 (3题)" if x == "demo" else "完整模式 (全部)"
        )
        
        st.markdown("---")
        
        # 候选人配置
        st.subheader("👤 候选人配置")
        
        candidate_type = st.radio(
            "候选人来源",
            options=["模板候选人", "随机生成"]
        )
        
        if candidate_type == "模板候选人":
            template_name = st.selectbox(
                "选择模板",
                options=templates,
                format_func=lambda x: {
                    'ideal_candidate': '⭐ 理想候选人',
                    'junior_candidate': '👶 初级候选人',
                    'nervous_candidate': '😰 紧张型',
                    'overconfident_candidate': '😎 过度自信',
                    'underconfident_candidate': '😔 过度谦虚',
                    'test_react_blind_spot': '🧪 React知识盲区测试'
                }.get(x, x)
            )
        else:
            strategy = st.selectbox(
                "性格生成策略",
                options=["normal", "balanced", "extreme", "uniform"],
                format_func=lambda x: {
                    'normal': '正态分布（推荐）',
                    'balanced': '平衡型',
                    'extreme': '极端型',
                    'uniform': '完全随机'
                }.get(x, x)
            )
            
            archetype = st.selectbox(
                "性格原型",
                options=["random", "confident", "anxious", "creative", "reliable", "friendly", "analytical"],
                format_func=lambda x: {
                    'random': '随机',
                    'confident': '自信型',
                    'anxious': '焦虑型',
                    'creative': '创造型',
                    'reliable': '可靠型',
                    'friendly': '友善型',
                    'analytical': '分析型'
                }.get(x, x)
            )
        
        st.markdown("---")
        
        # 批量模拟
        batch_size = st.number_input(
            "🔢 批量模拟数量",
            min_value=1,
            max_value=10,
            value=1,
            help="设置一次自动执行多少个面试"
        )
    
    # 主区域 - 分两栏
    col_control, col_display = st.columns([1, 2])
    
    # 左侧 - 控制面板
    with col_control:
        st.subheader("🎛️ 控制面板")
        
        # 控制按钮
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ 开始面试", use_container_width=True, type="primary", disabled=st.session_state.interview_running):
                # 批量生成候选人配置
                candidate_configs = []
                
                with st.spinner(f"正在生成 {batch_size} 个候选人配置..."):
                    for _ in range(batch_size):
                        if candidate_type == "模板候选人":
                            config = generate_candidate_config(
                                candidate_type, template_name, domain_id, None, None
                            )
                        else:
                            config = generate_candidate_config(
                                candidate_type, None, domain_id, strategy, 
                                archetype if archetype != "random" else None
                            )
                        candidate_configs.append(config)
                
                # 清空之前的消息
                st.session_state.messages = []
                st.session_state.final_report = None
                st.session_state.candidate_info = None
                st.session_state.resume_data = None
                st.session_state.interview_info = None
                
                # 启动面试（传入配置列表）
                st.session_state.controller.start_interview(
                    domain_id=domain_id,
                    candidate_configs=candidate_configs,
                    mode=mode
                )
                st.session_state.interview_running = True
                st.rerun()
        
        with col2:
            if st.button("⏹️ 中止", use_container_width=True, disabled=not st.session_state.interview_running):
                st.session_state.controller.stop_interview()
                st.session_state.interview_running = False
                st.rerun()
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("⏸️ 暂停", use_container_width=True, disabled=not st.session_state.interview_running):
                st.session_state.controller.pause_interview()
                st.rerun()
        
        with col4:
            if st.button("⏯️ 继续", use_container_width=True, disabled=not st.session_state.interview_running):
                st.session_state.controller.resume_interview()
                st.rerun()
        
        st.markdown("---")
        
        # 状态显示
        st.subheader("📊 状态")
        
        status_text = "🟢 运行中" if st.session_state.interview_running else "⚪ 空闲"
        st.markdown(f"**面试状态:** {status_text}")
        
        if st.session_state.controller.is_paused:
            st.warning("⏸️ 已暂停")
        
        st.markdown("---")
        
        # 候选人信息卡片
        if st.session_state.candidate_info:
            st.subheader("👤 候选人信息")
            info = st.session_state.candidate_info
            
            st.markdown(f"""
            <div class="candidate-card">
                <h3>{info.get('name', '未知')}</h3>
                <p><strong>技能数量:</strong> {len(info.get('skills', {}))}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示技能
            with st.expander("📚 技能详情"):
                skills = info.get('skills', {})
                for skill, level in list(skills.items())[:10]:
                    st.progress(level / 10, text=f"{skill}: {level}/10")
            
            # 显示性格
            if 'personality' in info and info['personality']:
                with st.expander("🎭 性格特征"):
                    personality = info['personality']
                    st.write(f"- 开放性: {personality.get('openness', 0.5):.2f}")
                    st.write(f"- 尽责性: {personality.get('conscientiousness', 0.5):.2f}")
                    st.write(f"- 外向性: {personality.get('extraversion', 0.5):.2f}")
                    st.write(f"- 宜人性: {personality.get('agreeableness', 0.5):.2f}")
                    st.write(f"- 神经质: {personality.get('neuroticism', 0.5):.2f}")
        
        # 简历信息
        if st.session_state.resume_data:
            st.markdown("---")
            with st.expander("📄 查看简历"):
                resume = st.session_state.resume_data
                st.markdown(f"**姓名:** {resume.get('name', '')}")
                st.markdown(f"**邮箱:** {resume.get('email', '')}")
                st.markdown(f"**电话:** {resume.get('phone', '')}")
                
                if 'work_experience' in resume:
                    st.markdown("**工作经验:**")
                    for exp in resume['work_experience'][:2]:
                        st.markdown(f"- {exp.get('position', '')} @ {exp.get('company', '')}")
    
    # 右侧 - 面试显示区
    with col_display:
        st.subheader("💬 面试对话")
        
        # 面试信息横幅
        if st.session_state.interview_info:
            info = st.session_state.interview_info
            st.info(f"🏢 **{info.get('company', '')}** | 💼 **{info.get('job_title', '')}** | 👤 **{info.get('candidate_name', '')}**")
        
        # 消息显示容器
        message_container = st.container()
        
        with message_container:
            # 显示所有消息
            for msg in st.session_state.messages:
                msg_type = msg.get('type', '')
                
                if msg_type == 'message':
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    metadata = msg.get('metadata', {})
                    
                    if role == 'interviewer':
                        icon = "🔍" if metadata.get('is_followup') else "👔"
                        st.markdown(f"""
                        <div class="message-box interviewer-msg">
                            <strong>{icon} 面试官:</strong><br>
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif role == 'candidate':
                        st.markdown(f"""
                        <div class="message-box candidate-msg">
                            <strong>👤 候选人:</strong><br>
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
                
                elif msg_type == 'system':
                    st.markdown(f"""
                    <div class="message-box system-msg">
                        <strong>📢 系统:</strong> {msg.get('content', '')}
                    </div>
                    """, unsafe_allow_html=True)
                
                elif msg_type == 'evaluation':
                    eval_data = msg.get('content', {})
                    score = eval_data.get('score', 0)
                    recommendation = eval_data.get('recommendation', '')
                    is_followup = eval_data.get('is_followup', False)
                    
                    label = "追问评分" if is_followup else "评分"
                    
                    # 颜色映射
                    if score >= 80:
                        color = "#10b981"
                    elif score >= 60:
                        color = "#f59e0b"
                    else:
                        color = "#ef4444"
                    
                    st.markdown(f"""
                    <div class="eval-box">
                        <strong>📊 {label}:</strong> 
                        <span style="color: {color}; font-size: 1.5rem; font-weight: bold;">{score:.1f}/100</span>
                        <span style="color: {color};">({recommendation})</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 最终报告
        if st.session_state.final_report:
            st.markdown("---")
            st.subheader("📊 最终评估报告")
            
            report = st.session_state.final_report
            
            # 推荐度评分
            score = report.get('recommendation_score', 0)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # 评分仪表盘
                fig = create_score_chart(score, "综合推荐度")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 维度雷达图
                if 'dimension_scores_summary' in report:
                    fig = create_dimension_radar_chart(report['dimension_scores_summary'])
                    st.plotly_chart(fig, use_container_width=True)
            
            # 技能评分
            if 'skill_scores' in report:
                st.markdown("#### 💪 技能评分")
                fig = create_skills_bar_chart(report['skill_scores'])
                st.plotly_chart(fig, use_container_width=True)
            
            # 文字报告
            col1, col2 = st.columns(2)
            
            with col1:
                if 'strengths' in report:
                    st.markdown("#### ✨ 优势")
                    for strength in report['strengths']:
                        st.success(f"✓ {strength}")
            
            with col2:
                if 'improvements' in report:
                    st.markdown("#### 📈 改进建议")
                    for improvement in report['improvements']:
                        st.warning(f"• {improvement}")
            
            # 总结
            if 'summary' in report:
                st.markdown("#### 📝 总结")
                st.info(report['summary'])
            
            # 招聘建议
            if 'recommendation' in report:
                st.markdown("#### 🎯 招聘建议")
                st.markdown(f"**{report['recommendation']}**")
    
    # 自动刷新消息
    if st.session_state.interview_running:
        # 从控制器获取新消息
        while True:
            msg = st.session_state.controller.get_message()
            if msg is None:
                break
            
            msg_type = msg.get('type', '')
            
            # 保存消息
            if msg_type in ['message', 'system', 'evaluation']:
                st.session_state.messages.append(msg)
            
            # 处理特殊消息
            if msg_type == 'candidate_info':
                st.session_state.candidate_info = msg.get('content', {})
            elif msg_type == 'resume':
                st.session_state.resume_data = msg.get('content', {})
            elif msg_type == 'interview_info':
                st.session_state.interview_info = msg.get('content', {})
            elif msg_type == 'final_report':
                st.session_state.final_report = msg.get('content', {})
                st.session_state.interview_running = False
            elif msg_type == 'error':
                st.error(msg.get('content', ''))
                st.session_state.interview_running = False
        
        # 刷新页面
        time.sleep(0.5)
        st.rerun()


if __name__ == "__main__":
    main()
