"""
域配置页面
添加和管理新的面试领域（开发中）
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from frontend.data_loader import DataLoader

# 页面配置
st.set_page_config(
    page_title="域配置 - HRM1",
    page_icon="⚙️",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    .dev-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin: 2rem 0;
    }
    .feature-list {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .domain-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        margin: 1rem 0;
        transition: all 0.3s;
    }
    .domain-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("⚙️ 域配置管理")
    st.markdown("添加和配置新的面试领域")
    st.markdown("---")
    
    # 开发中横幅
    st.markdown("""
    <div class="dev-banner">
        <h1>🚧 功能开发中 🚧</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            此页面功能正在开发中，敬请期待！<br>
            未来将支持完整的领域配置管理功能
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 当前支持的领域
    st.subheader("📋 当前支持的领域")
    
    loader = DataLoader()
    domains = loader.load_domains()
    
    cols = st.columns(3)
    
    domain_info_map = {
        'tech': {
            'name': '💻 技术领域',
            'description': '软件开发、系统架构、数据科学等技术岗位',
            'skills': ['Python', 'Java', 'React', 'MySQL', '微服务', '算法'],
            'color': '#3b82f6'
        },
        'marketing': {
            'name': '📢 营销领域',
            'description': '数字营销、品牌策划、内容运营等营销岗位',
            'skills': ['SEO', 'SEM', '社交媒体', '数据分析', '内容创作', '品牌策略'],
            'color': '#f59e0b'
        },
        'healthcare': {
            'name': '🏥 医疗领域',
            'description': '临床医疗、护理、医疗管理等医疗岗位',
            'skills': ['临床诊断', '患者护理', '医疗法规', '病历管理', '急救', '药理学'],
            'color': '#10b981'
        }
    }
    
    for i, domain_id in enumerate(domains):
        with cols[i % 3]:
            info = domain_info_map.get(domain_id, {
                'name': domain_id,
                'description': '自定义领域',
                'skills': [],
                'color': '#6b7280'
            })
            
            st.markdown(f"""
            <div class="domain-card">
                <h3>{info['name']}</h3>
                <p style="color: #64748b;">{info['description']}</p>
                <p style="margin-top: 1rem;"><strong>核心技能:</strong></p>
                <p style="color: {info['color']};">{', '.join(info['skills'][:4])}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 规划的功能
    st.subheader("🎯 规划的功能")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-list">
            <h4>📝 领域配置</h4>
            <ul>
                <li>添加新的面试领域</li>
                <li>配置领域基本信息</li>
                <li>设置适用行业和角色</li>
                <li>定义评估维度</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-list">
            <h4>🧠 技能树管理</h4>
            <ul>
                <li>创建技能分类体系</li>
                <li>定义技能等级标准</li>
                <li>设置技能权重</li>
                <li>管理技能依赖关系</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-list">
            <h4>🔍 信号词配置</h4>
            <ul>
                <li>设置高级术语词库</li>
                <li>配置模糊词汇检测</li>
                <li>定义露怯指标词</li>
                <li>管理技术指标词</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-list">
            <h4>❓ 问题模板</h4>
            <ul>
                <li>创建问题模板库</li>
                <li>设置问题难度等级</li>
                <li>配置问题类别</li>
                <li>关联评估信号</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 临时配置预览
    st.subheader("🔧 配置预览（示例）")
    
    with st.expander("查看技术领域配置示例"):
        st.markdown("""
        #### 领域基本信息
        - **领域ID**: tech
        - **领域名称**: 技术领域  
        - **描述**: 涵盖软件开发、系统架构、数据科学等技术相关岗位
        - **适用行业**: 互联网、软件、IT服务、金融科技等
        
        #### 技能分类
        **1. 编程语言** (权重: 0.25)
        - Python (初级/中级/高级/专家)
        - Java (初级/中级/高级/专家)
        - JavaScript (初级/中级/高级/专家)
        
        **2. 框架与工具** (权重: 0.20)
        - React, Vue, Angular
        - Spring Boot, Django, Flask
        - Docker, Kubernetes
        
        **3. 数据库** (权重: 0.15)
        - MySQL, PostgreSQL
        - MongoDB, Redis
        - 数据库设计与优化
        
        #### 评估信号词
        **高级术语**: 微服务架构, 分布式系统, 负载均衡, 容器化, CI/CD...
        
        **模糊词汇**: 大概, 应该, 可能, 好像, 一般来说...
        
        **露怯指标**: 不太了解, 没怎么用过, 只是听说过...
        
        **技术指标**: QPS, TPS, 延迟, 吞吐量, 可用性...
        """)
    
    st.markdown("---")
    
    # 临时表单（不可用）
    st.subheader("➕ 添加新领域（开发中）")
    
    with st.form("add_domain_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            domain_id = st.text_input("领域ID", placeholder="例如: finance", disabled=True)
            domain_name = st.text_input("领域名称", placeholder="例如: 金融领域", disabled=True)
        
        with col2:
            applicable_industries = st.text_input("适用行业", placeholder="用逗号分隔", disabled=True)
            typical_roles = st.text_input("典型角色", placeholder="用逗号分隔", disabled=True)
        
        description = st.text_area("领域描述", disabled=True)
        
        submit = st.form_submit_button("保存配置", disabled=True)
        
        if submit:
            st.warning("此功能正在开发中，暂不可用")
    
    st.markdown("---")
    
    # 开发计划
    st.subheader("📅 开发计划")
    
    st.markdown("""
    该功能预计在后续版本中实现：
    
    - **v1.1**: 基础领域配置界面，支持添加新领域
    - **v1.2**: 技能树可视化管理
    - **v1.3**: 信号词智能配置
    - **v2.0**: 完整的领域配置生态系统
    
    敬请期待！
    """)
    
    # 页脚
    st.markdown("---")
    st.info("💡 如需添加新领域，请参考 `domains/` 目录下的配置文件格式手动创建")


if __name__ == "__main__":
    main()
