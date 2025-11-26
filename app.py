"""
HR 智能面试系统 M1A5 - Streamlit前端主页
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 页面配置
st.set_page_config(
    page_title="HR 智能面试系统 M1A5",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .feature-card h3 {
        color: white;
        margin-bottom: 0.5rem;
    }
    .stat-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 主页内容
def main():
    # 标题
    st.markdown('<h1 class="main-header">🎯 HR 智能面试系统 M1A5</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 欢迎信息
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>🚀 欢迎使用智能面试系统</h2>
            <p style="font-size: 1.2rem; color: #64748b;">
                基于AI技术的下一代面试解决方案<br>
                支持跨行业领域 | 智能追问 | 知识盲区检测
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 功能特性
    st.markdown("### ✨ 核心功能")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎮 面试控制台</h3>
            <p>实时模拟面试流程<br>
            • 选择公司与领域<br>
            • 批量模拟候选人<br>
            • 流式对话输出<br>
            • 开始/暂停/继续/中止</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>📊 历史记录</h3>
            <p>深度分析面试数据<br>
            • 查看历史面试<br>
            • 评估系统能力<br>
            • 图表可视化<br>
            • 数据导出</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>⚙️ 域配置</h3>
            <p>自定义面试领域<br>
            • 添加新领域<br>
            • 配置技能树<br>
            • 信号词设置<br>
            • 问题模板</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 快速开始
    st.markdown("### 🚀 快速开始")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        #### 📝 使用步骤：
        
        1. **面试控制台** - 点击侧边栏进入面试控制台
        2. **选择配置** - 选择公司、领域和候选人类型
        3. **开始面试** - 点击"开始面试"按钮
        4. **实时查看** - 观察面试过程和评估结果
        5. **查看历史** - 在历史记录页面分析所有面试数据
        
        #### 🎯 系统特色：
        
        - **跨行业支持**：技术、营销、医疗等多个领域
        - **智能追问机制**：自动检测知识盲区并深入提问
        - **多维度评分**：技术深度、实践经验、沟通能力等6个维度
        - **实时流式输出**：模拟真实面试的流畅体验
        """)
    
    with col2:
        # 系统状态
        st.markdown("#### 📈 系统概览")
        
        # 加载统计数据
        try:
            from frontend.data_loader import DataLoader
            loader = DataLoader()
            stats = loader.get_statistics()
            
            st.markdown(f"""
            <div class="stat-box">
                <h4>📊 总面试次数</h4>
                <h2>{stats.get('total_interviews', 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-box">
                <h4>⭐ 平均评分</h4>
                <h2>{stats.get('avg_score', 0):.1f}/100</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-box">
                <h4>⏱️ 平均时长</h4>
                <h2>{stats.get('avg_duration', 0):.1f} 分钟</h2>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.info("💡 暂无面试数据，开始你的第一次面试吧！")
    
    st.markdown("---")
    
    # 导航提示
    st.markdown("### 🧭 导航指引")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("👈 **请使用左侧边栏** 切换不同功能页面")
    
    with col2:
        st.success("✅ **面试控制台** 开始第一次模拟面试")
    
    with col3:
        st.warning("📊 **历史记录** 查看和分析面试数据")
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; padding: 2rem 0;">
        <p>HR 智能面试系统 M1A5 | 基于大语言模型的智能面试解决方案</p>
        <p>支持的领域：技术 | 营销 | 医疗 | ...</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
