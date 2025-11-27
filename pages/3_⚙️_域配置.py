"""
域配置页面
添加和管理新的面试领域
"""

import streamlit as st
from pathlib import Path
import sys
import json
import re
from typing import Dict, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.domain_generator import DomainConfigGenerator
from domains import list_available_domains

# 页面配置
st.set_page_config(
    page_title="域配置 - HRM1",
    page_icon="⚙️",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    .domain-selector {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    .ai-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .config-tab {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    .success-banner {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #10b981;
    }
    .error-banner {
        background: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #ef4444;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """初始化session state"""
    if 'domain_configs' not in st.session_state:
        st.session_state.domain_configs = None
    if 'current_domain_id' not in st.session_state:
        st.session_state.current_domain_id = None
    if 'is_editing_existing' not in st.session_state:
        st.session_state.is_editing_existing = False
    if 'ai_generating' not in st.session_state:
        st.session_state.ai_generating = False


def generate_domain_id(domain_name: str) -> str:
    """从领域名称生成domain_id"""
    # 移除特殊字符，转换为拼音或英文
    # 简单实现：使用小写字母和下划线
    clean_name = re.sub(r'[^\w\s]', '', domain_name)
    domain_id = re.sub(r'\s+', '_', clean_name.strip().lower())
    return domain_id if domain_id else 'new_domain'


def render_ai_generation_section():
    """渲染AI生成区域"""
    st.markdown("""
    <div class="ai-section">
        <h3 style="margin-top: 0;">🤖 AI智能填充</h3>
        <p>输入公司和业务描述，让AI为您生成完整的领域配置</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        business_desc = st.text_area(
            "公司/业务描述",
            placeholder="例如：一家专注于供应链管理的SaaS公司，主要服务制造业客户，提供从采购到交付的全流程数字化解决方案...",
            height=120,
            key="business_desc_input"
        )
    
    with col2:
        st.markdown("##### 或使用模板")
        template_options = {
            "无": None,
            "金融科技": "一家金融科技公司，专注于智能风控和信贷评估系统的研发",
            "教育科技": "一家在线教育平台，提供K12和职业教育课程，拥有自研的学习管理系统",
            "电商零售": "一家跨境电商平台，专注于东南亚市场，提供供应链和物流服务"
        }
        selected_template = st.selectbox("选择模板", list(template_options.keys()))
        
        if selected_template != "无" and st.button("📋 应用模板", use_container_width=True):
            st.session_state.business_desc_input = template_options[selected_template]
            st.rerun()
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 6])
    
    with col_btn1:
        if st.button("🎨 AI生成配置", type="primary", use_container_width=True):
            if not business_desc or len(business_desc.strip()) < 20:
                st.error("请输入至少20字的业务描述")
            else:
                # 使用status容器显示生成进度
                with st.status("🤖 AI正在生成配置（预计需要1-2分钟）...", expanded=True) as status:
                    try:
                        generator = DomainConfigGenerator()
                        
                        # 步骤1
                        st.write("📋 **步骤1/3**: 生成基础信息和技能体系...")
                        st.caption("正在分析业务特点，生成领域配置和技能分类...")
                        step1_result = generator._generate_domain_and_skills(business_desc)
                        st.success("✅ 步骤1完成 - 已生成领域基础信息和技能体系")
                        
                        # 步骤2
                        st.write("❓ **步骤2/3**: 生成问题模板...")
                        st.caption("基于技能体系，生成面试问题模板（含占位符）...")
                        step2_result = generator._generate_question_templates(
                            business_desc,
                            step1_result['domain_config'],
                            step1_result['skills_taxonomy']
                        )
                        st.success("✅ 步骤2完成 - 已生成问题模板和追问模板")
                        
                        # 步骤3
                        st.write("🔍 **步骤3/3**: 生成评估信号词...")
                        st.caption("生成用于评估候选人回答质量的关键信号词...")
                        step3_result = generator._generate_assessment_signals(
                            business_desc,
                            step1_result['domain_config']
                        )
                        st.success("✅ 步骤3完成 - 已生成评估信号词")
                        
                        # 合并结果
                        configs = {
                            'domain_config': step1_result['domain_config'],
                            'skills_taxonomy': step1_result['skills_taxonomy'],
                            'question_templates': step2_result,
                            'assessment_signals': step3_result
                        }
                        
                        st.session_state.domain_configs = configs
                        st.session_state.current_domain_id = configs['domain_config'].get('domain_id', 'new_domain')
                        st.session_state.is_editing_existing = False
                        
                        status.update(label="✅ AI生成完成！", state="complete", expanded=False)
                        st.success("✅ AI生成完成！请在下方编辑和保存配置")
                        st.rerun()
                    except Exception as e:
                        status.update(label="❌ 生成失败", state="error", expanded=True)
                        st.error(f"❌ 生成失败: {str(e)}")
    
    with col_btn2:
        if st.button("🆕 空白配置", use_container_width=True):
            generator = DomainConfigGenerator()
            st.session_state.domain_configs = generator.get_default_config_template()
            st.session_state.current_domain_id = 'new_domain'
            st.session_state.is_editing_existing = False
            st.rerun()


def render_domain_selector():
    """渲染域选择器"""
    st.markdown("### 📁 现有域管理")
    
    domains = list_available_domains()
    
    if domains:
        cols = st.columns(len(domains) + 1)
        
        for i, domain_id in enumerate(domains):
            with cols[i]:
                if st.button(f"📝 {domain_id}", use_container_width=True):
                    generator = DomainConfigGenerator()
                    configs = generator.load_domain_config(domain_id)
                    if configs:
                        st.session_state.domain_configs = configs
                        st.session_state.current_domain_id = domain_id
                        st.session_state.is_editing_existing = True
                        st.rerun()
        
        with cols[len(domains)]:
            if st.button("➕ 新建域", use_container_width=True, type="primary"):
                generator = DomainConfigGenerator()
                st.session_state.domain_configs = generator.get_default_config_template()
                st.session_state.current_domain_id = 'new_domain'
                st.session_state.is_editing_existing = False
                st.rerun()
    else:
        if st.button("➕ 创建第一个域", type="primary"):
            generator = DomainConfigGenerator()
            st.session_state.domain_configs = generator.get_default_config_template()
            st.session_state.current_domain_id = 'new_domain'
            st.session_state.is_editing_existing = False
            st.rerun()


def render_basic_info_tab(config: Dict):
    """渲染基本信息Tab"""
    st.markdown("### 📋 领域基本信息")
    
    # 获取当前域ID作为key后缀（如果是新建则用timestamp）
    domain_key = config.get('domain_id', '') or st.session_state.get('current_domain_id', 'new')
    
    # 领域名称
    st.markdown("#### 基本信息")
    domain_name = st.text_input(
        "领域名称*",
        value=config.get('domain_name', ''),
        placeholder="例如: 金融科技",
        key=f"domain_name_{domain_key}"
    )
    
    # 自动生成domain_id
    if domain_name:
        suggested_id = generate_domain_id(domain_name)
        domain_id = st.text_input(
            "领域ID*",
            value=config.get('domain_id', suggested_id),
            placeholder="例如: fintech",
            help="小写英文字母和下划线，自动从名称生成",
            key=f"domain_id_{domain_key}"
        )
    else:
        domain_id = st.text_input(
            "领域ID*",
            value=config.get('domain_id', ''),
            placeholder="例如: fintech",
            key=f"domain_id_alt_{domain_key}"
        )
    
    description = st.text_area(
        "领域描述*",
        value=config.get('description', ''),
        placeholder="详细描述该领域的特点和范围",
        height=100,
        key=f"description_{domain_key}"
    )
    
    st.markdown("---")
    
    # 适用行业
    st.markdown("#### 适用行业")
    industries = config.get('applicable_industries', [])
    industries_str = ", ".join(industries) if isinstance(industries, list) else ""
    industries_input = st.text_input(
        "输入行业（用逗号分隔）",
        value=industries_str,
        placeholder="互联网, 软件开发, 人工智能, 云计算",
        key=f"industries_{domain_key}"
    )
    
    # 典型角色
    st.markdown("#### 典型角色")
    roles = config.get('typical_roles', [])
    roles_str = ", ".join(roles) if isinstance(roles, list) else ""
    roles_input = st.text_input(
        "输入角色（用逗号分隔）",
        value=roles_str,
        placeholder="软件工程师, 架构师, 产品经理",
        key=f"roles_{domain_key}"
    )
    
    # 典型项目
    st.markdown("#### 典型项目")
    projects = config.get('typical_projects', [])
    projects_str = ", ".join(projects) if isinstance(projects, list) else ""
    projects_input = st.text_area(
        "输入项目（用逗号分隔）",
        value=projects_str,
        placeholder="企业管理系统, 电商平台开发, 数据分析平台",
        height=80,
        key=f"projects_{domain_key}"
    )
    
    # 典型成就
    st.markdown("#### 典型成就")
    achievements = config.get('typical_achievements', [])
    achievements_str = ", ".join(achievements) if isinstance(achievements, list) else ""
    achievements_input = st.text_area(
        "输入成就（用逗号分隔）",
        value=achievements_str,
        placeholder="完成核心功能开发, 性能优化提升3倍, 主导系统架构设计",
        height=80,
        key=f"achievements_{domain_key}"
    )
    
    # 更新配置
    config['domain_name'] = domain_name
    config['domain_id'] = domain_id
    config['description'] = description
    config['applicable_industries'] = [s.strip() for s in industries_input.split(',') if s.strip()]
    config['typical_roles'] = [s.strip() for s in roles_input.split(',') if s.strip()]
    config['typical_projects'] = [s.strip() for s in projects_input.split(',') if s.strip()]
    config['typical_achievements'] = [s.strip() for s in achievements_input.split(',') if s.strip()]


def render_skills_tab(config: Dict):
    """渲染技能体系Tab"""
    st.markdown("### 🛠️ 技能分类体系")
    
    skill_categories = config.get('skill_categories', {})
    
    # 处理列表格式的skill_categories（AI可能生成列表而不是字典）
    if isinstance(skill_categories, list):
        # 将列表转换为字典格式
        dict_categories = {}
        for i, cat in enumerate(skill_categories):
            if isinstance(cat, dict):
                cat_id = cat.get('id', f'category_{i}')
                dict_categories[cat_id] = {
                    'name': cat.get('name', f'分类{i+1}'),
                    'skills': cat.get('skills', []),
                    'description': cat.get('description', '')
                }
        skill_categories = dict_categories
        config['skill_categories'] = skill_categories
    
    # 添加新分类
    with st.expander("➕ 添加技能分类"):
        col1, col2 = st.columns(2)
        with col1:
            new_cat_id = st.text_input("分类ID", placeholder="backend")
            new_cat_name = st.text_input("分类名称", placeholder="后端开发")
        with col2:
            new_cat_desc = st.text_input("分类描述", placeholder="服务器端开发技能")
            new_cat_skills = st.text_input("技能列表", placeholder="python, java, go")
        
        if st.button("添加分类"):
            if new_cat_id and new_cat_name:
                skill_categories[new_cat_id] = {
                    "name": new_cat_name,
                    "skills": [s.strip() for s in new_cat_skills.split(',') if s.strip()],
                    "description": new_cat_desc
                }
                st.success(f"✅ 已添加分类: {new_cat_name}")
                st.rerun()
    
    # 编辑现有分类
    if skill_categories and isinstance(skill_categories, dict):
        for cat_id, cat_data in list(skill_categories.items()):
            with st.expander(f"📂 {cat_data.get('name', cat_id)}"):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    cat_name = st.text_input("分类名称", value=cat_data.get('name', ''), key=f"cat_name_{cat_id}")
                    cat_desc = st.text_input("描述", value=cat_data.get('description', ''), key=f"cat_desc_{cat_id}")
                    skills_list = cat_data.get('skills', [])
                    skills_str = ", ".join(skills_list) if isinstance(skills_list, list) else ""
                    cat_skills = st.text_input("技能列表（逗号分隔）", value=skills_str, key=f"cat_skills_{cat_id}")
                    
                    # 更新数据
                    skill_categories[cat_id]['name'] = cat_name
                    skill_categories[cat_id]['description'] = cat_desc
                    skill_categories[cat_id]['skills'] = [s.strip() for s in cat_skills.split(',') if s.strip()]
                
                with col2:
                    if st.button("🗑️ 删除", key=f"del_{cat_id}"):
                        del skill_categories[cat_id]
                        st.rerun()
    
    st.markdown("---")
    
    # 软技能
    st.markdown("### 🧠 软技能")
    soft_skills = config.get('soft_skills', {})
    
    # 获取当前域ID作为key后缀
    domain_key = st.session_state.get('current_domain_id', 'new')
    
    # 处理列表格式的soft_skills
    if isinstance(soft_skills, list):
        dict_soft_skills = {}
        for i, skill in enumerate(soft_skills):
            if isinstance(skill, dict):
                skill_id = skill.get('id', f'soft_skill_{i}')
                skill_name = skill.get('name', f'软技能{i+1}')
                dict_soft_skills[skill_id] = skill_name
            elif isinstance(skill, str):
                dict_soft_skills[f'soft_skill_{i}'] = skill
        soft_skills = dict_soft_skills
        config['soft_skills'] = soft_skills
    
    # 添加新软技能
    with st.expander("➕ 添加软技能"):
        col1, col2 = st.columns(2)
        with col1:
            new_soft_id = st.text_input("软技能ID", placeholder="communication", key=f"new_soft_id_{domain_key}")
        with col2:
            new_soft_name = st.text_input("软技能名称", placeholder="沟通能力", key=f"new_soft_name_{domain_key}")
        
        if st.button("添加软技能", key=f"add_soft_skill_{domain_key}"):
            if new_soft_id and new_soft_name:
                soft_skills[new_soft_id] = new_soft_name
                st.success(f"✅ 已添加软技能: {new_soft_name}")
                st.rerun()
    
    # 编辑现有软技能（采用卡片式显示，更直观）
    if soft_skills and isinstance(soft_skills, dict):
        st.markdown("#### 已有软技能")
        
        # 显示列标题
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.markdown("**技能ID**")
        with col2:
            st.markdown("**技能名称**")
        with col3:
            st.markdown("**操作**")
        
        # 使用列表方式显示，每个软技能一行，可以编辑和删除
        skills_to_delete = []
        updated_soft_skills = {}
        
        for idx, (skill_id, skill_name) in enumerate(list(soft_skills.items())):
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                new_id = st.text_input(
                    f"ID_{idx}", 
                    value=skill_id, 
                    key=f"soft_id_{skill_id}_{domain_key}",
                    label_visibility="collapsed",
                    placeholder="skill_id"
                )
            
            with col2:
                new_name = st.text_input(
                    f"Name_{idx}", 
                    value=skill_name, 
                    key=f"soft_name_{skill_id}_{domain_key}",
                    label_visibility="collapsed",
                    placeholder="软技能名称"
                )
            
            with col3:
                st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_soft_{skill_id}_{domain_key}", help="删除此软技能"):
                    skills_to_delete.append(skill_id)
                    continue
            
            # 如果ID改变了，需要特殊处理
            if new_id != skill_id:
                updated_soft_skills[new_id] = new_name
                skills_to_delete.append(skill_id)
            else:
                updated_soft_skills[skill_id] = new_name
        
        # 应用删除和更新
        for skill_id in skills_to_delete:
            if skill_id in soft_skills and skill_id not in updated_soft_skills:
                pass  # 真正的删除
            else:
                pass  # ID改变导致的"删除"
        
        # 合并更新
        soft_skills.clear()
        soft_skills.update(updated_soft_skills)
        config['soft_skills'] = soft_skills
        
        if skills_to_delete:
            st.rerun()
    else:
        st.info("暂无软技能，点击上方➕添加")
    
    config['skill_categories'] = skill_categories


def render_questions_tab(config: Dict):
    """渲染问题模板Tab"""
    st.markdown("### ❓ 问题模板配置")
    
    # 获取当前域ID作为key后缀
    domain_key = st.session_state.get('current_domain_id', 'new')
    
    templates_by_level = config.get('templates_by_skill_level', {})
    
    # 基础级问题
    st.markdown("#### 基础级问题")
    basic_templates = templates_by_level.get('basic', {})
    # 处理列表格式：如果直接是列表，就当作patterns；如果是字典，取patterns字段
    if isinstance(basic_templates, list):
        basic_patterns = basic_templates
    elif isinstance(basic_templates, dict):
        basic_patterns = basic_templates.get('patterns', [])
    else:
        basic_patterns = []
    basic_str = "\n".join(basic_patterns) if isinstance(basic_patterns, list) else ""
    basic_input = st.text_area(
        "基础问题模板（每行一个）",
        value=basic_str,
        height=120,
        placeholder="请介绍一下你对{skill}的理解\n你在项目中如何使用{skill}的？",
        key=f"basic_questions_{domain_key}"
    )
    templates_by_level['basic'] = {
        "description": "基础级别问题",
        "patterns": [line.strip() for line in basic_input.split('\n') if line.strip()]
    }
    
    # 中级问题
    st.markdown("#### 中级问题")
    inter_templates = templates_by_level.get('intermediate', {})
    if isinstance(inter_templates, list):
        inter_patterns = inter_templates
    elif isinstance(inter_templates, dict):
        inter_patterns = inter_templates.get('patterns', [])
    else:
        inter_patterns = []
    inter_str = "\n".join(inter_patterns) if isinstance(inter_patterns, list) else ""
    inter_input = st.text_area(
        "中级问题模板（每行一个）",
        value=inter_str,
        height=120,
        key=f"inter_questions_{domain_key}"
    )
    templates_by_level['intermediate'] = {
        "description": "中级问题",
        "patterns": [line.strip() for line in inter_input.split('\n') if line.strip()]
    }
    
    # 高级问题
    st.markdown("#### 高级问题")
    adv_templates = templates_by_level.get('advanced', {})
    if isinstance(adv_templates, list):
        adv_patterns = adv_templates
    elif isinstance(adv_templates, dict):
        adv_patterns = adv_templates.get('patterns', [])
    else:
        adv_patterns = []
    adv_str = "\n".join(adv_patterns) if isinstance(adv_patterns, list) else ""
    adv_input = st.text_area(
        "高级问题模板（每行一个）",
        value=adv_str,
        height=120,
        key=f"adv_questions_{domain_key}"
    )
    templates_by_level['advanced'] = {
        "description": "高级问题",
        "patterns": [line.strip() for line in adv_input.split('\n') if line.strip()]
    }
    
    config['templates_by_skill_level'] = templates_by_level
    
    st.markdown("---")
    
    # 追问模板
    st.markdown("#### 追问模板")
    st.info("💡 追问模板用于面试官深入考察候选人的真实能力，包括三大类别")
    
    followup_templates = config.get('followup_templates', {})
    
    # 深入追问
    with st.expander("🔍 深入追问 (probe_depth)", expanded=False):
        st.caption("测试候选人对概念的真实理解深度")
        probe_data = followup_templates.get('probe_depth', {})
        if isinstance(probe_data, list):
            probe_patterns = probe_data
        elif isinstance(probe_data, dict):
            probe_patterns = probe_data.get('patterns', [])
        else:
            probe_patterns = []
        probe_str = "\n".join(probe_patterns) if isinstance(probe_patterns, list) else ""
        probe_input = st.text_area(
            "深入追问模板（每行一个）",
            value=probe_str,
            height=100,
            placeholder="能具体说说{mentioned_concept}的工作原理吗？\n你提到了{term}，能展开讲讲吗？",
            key=f"probe_followup_{domain_key}"
        )
        followup_templates['probe_depth'] = {
            "description": "深入追问，测试真实理解深度",
            "patterns": [line.strip() for line in probe_input.split('\n') if line.strip()]
        }
    
    # 挑战弱点
    with st.expander("⚡ 挑战弱点 (challenge_weakness)", expanded=False):
        st.caption("针对模糊或不确定的回答进行挑战")
        challenge_data = followup_templates.get('challenge_weakness', {})
        if isinstance(challenge_data, list):
            challenge_patterns = challenge_data
        elif isinstance(challenge_data, dict):
            challenge_patterns = challenge_data.get('patterns', [])
        else:
            challenge_patterns = []
        challenge_str = "\n".join(challenge_patterns) if isinstance(challenge_patterns, list) else ""
        challenge_input = st.text_area(
            "挑战弱点模板（每行一个）",
            value=challenge_str,
            height=100,
            placeholder="你刚才说{vague_statement}，能具体解释一下吗？\n这个{concept}的关键细节是什么？",
            key=f"challenge_followup_{domain_key}"
        )
        followup_templates['challenge_weakness'] = {
            "description": "针对模糊回答进行挑战",
            "patterns": [line.strip() for line in challenge_input.split('\n') if line.strip()]
        }
    
    # 验证经验
    with st.expander("✅ 验证经验 (verify_experience)", expanded=False):
        st.caption("验证候选人是否有真实的实践经验")
        verify_data = followup_templates.get('verify_experience', {})
        if isinstance(verify_data, list):
            verify_patterns = verify_data
        elif isinstance(verify_data, dict):
            verify_patterns = verify_data.get('patterns', [])
        else:
            verify_patterns = []
        verify_str = "\n".join(verify_patterns) if isinstance(verify_patterns, list) else ""
        verify_input = st.text_area(
            "验证经验模板（每行一个）",
            value=verify_str,
            height=100,
            placeholder="你在项目中具体是怎么配置{technology}的？\n遇到{problem}时，排查的步骤是什么？",
            key=f"verify_followup_{domain_key}"
        )
        followup_templates['verify_experience'] = {
            "description": "验证实际经验",
            "patterns": [line.strip() for line in verify_input.split('\n') if line.strip()]
        }
    
    config['followup_templates'] = followup_templates
    
    st.markdown("---")
    
    # 场景化问题
    st.markdown("#### 场景化问题")
    scenario_questions = config.get('scenario_questions', {})
    if isinstance(scenario_questions, list):
        scenario_patterns = scenario_questions
    elif isinstance(scenario_questions, dict):
        scenario_patterns = scenario_questions.get('patterns', [])
    else:
        scenario_patterns = []
    scenario_str = "\n".join(scenario_patterns) if isinstance(scenario_patterns, list) else ""
    scenario_input = st.text_area(
        "场景化问题模板（每行一个）",
        value=scenario_str,
        height=100,
        placeholder="如果系统出现{problem}，你会如何排查和解决？\n假设需要支持{requirement}，你会如何设计？",
        key=f"scenario_questions_{domain_key}"
    )
    config['scenario_questions'] = {
        "description": "场景化问题模板",
        "patterns": [line.strip() for line in scenario_input.split('\n') if line.strip()]
    }


def render_signals_tab(config: Dict):
    """渲染评估信号Tab"""
    st.markdown("### 🔍 评估信号词配置")
    
    # 获取当前域ID作为key后缀
    domain_key = st.session_state.get('current_domain_id', 'new')
    
    # 辅助函数：安全获取terms
    def safe_get_terms(data):
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('terms', [])
        return []
    
    # 高级术语
    st.markdown("#### 高级专业术语")
    high_terms_data = config.get('high_level_terms', {})
    high_terms = safe_get_terms(high_terms_data)
    high_str = ", ".join(high_terms) if isinstance(high_terms, list) else ""
    high_input = st.text_input(
        "高级术语（逗号分隔）",
        value=high_str,
        placeholder="微服务, 分布式, 高并发, 架构",
        key=f"high_terms_{domain_key}"
    )
    config['high_level_terms'] = {
        "description": "高级专业术语",
        "terms": [s.strip() for s in high_input.split(',') if s.strip()]
    }
    
    # 技术指标
    st.markdown("#### 技术/专业指标")
    tech_metrics_data = config.get('technical_metrics', {})
    tech_metrics = safe_get_terms(tech_metrics_data)
    if not tech_metrics:
        concrete_metrics_data = config.get('concrete_metrics', {})
        tech_metrics = safe_get_terms(concrete_metrics_data)
    tech_str = ", ".join(tech_metrics) if isinstance(tech_metrics, list) else ""
    tech_input = st.text_input(
        "技术指标（逗号分隔）",
        value=tech_str,
        placeholder="QPS, TPS, 延迟, 吞吐量",
        key=f"tech_metrics_{domain_key}"
    )
    config['technical_metrics'] = {
        "description": "技术指标",
        "terms": [s.strip() for s in tech_input.split(',') if s.strip()]
    }
    
    # 具体证据词
    st.markdown("#### 具体证据类词汇")
    evidence_terms_data = config.get('concrete_evidence', {})
    evidence_terms = safe_get_terms(evidence_terms_data)
    evidence_str = ", ".join(evidence_terms) if isinstance(evidence_terms, list) else ""
    evidence_input = st.text_input(
        "证据词汇（逗号分隔）",
        value=evidence_str,
        placeholder="例如, 比如, 具体来说, 代码, 实现",
        key=f"evidence_terms_{domain_key}"
    )
    config['concrete_evidence'] = {
        "description": "具体证据类词汇",
        "terms": [s.strip() for s in evidence_input.split(',') if s.strip()]
    }
    
    st.markdown("---")
    
    # 模糊词汇
    st.markdown("#### 模糊词汇")
    vague_terms_data = config.get('vague_words', {})
    vague_terms = safe_get_terms(vague_terms_data)
    vague_str = ", ".join(vague_terms) if isinstance(vague_terms, list) else ""
    vague_input = st.text_input(
        "模糊词汇（逗号分隔）",
        value=vague_str,
        placeholder="大概, 应该, 可能, 好像",
        key=f"vague_terms_{domain_key}"
    )
    config['vague_words'] = {
        "description": "模糊词汇",
        "terms": [s.strip() for s in vague_input.split(',') if s.strip()]
    }
    
    # 露怯关键词
    st.markdown("#### 露怯关键词")
    weakness_terms_data = config.get('weakness_indicators', {})
    weakness_terms = safe_get_terms(weakness_terms_data)
    weakness_str = ", ".join(weakness_terms) if isinstance(weakness_terms, list) else ""
    weakness_input = st.text_input(
        "露怯关键词（逗号分隔）",
        value=weakness_str,
        placeholder="不太了解, 记不清, 不太确定",
        key=f"weakness_terms_{domain_key}"
    )
    config['weakness_indicators'] = {
        "description": "露怯关键词",
        "terms": [s.strip() for s in weakness_input.split(',') if s.strip()]
    }
    
    # 空话套话
    st.markdown("#### 空话套话")
    empty_terms_data = config.get('empty_phrases', {})
    empty_terms = safe_get_terms(empty_terms_data)
    empty_str = ", ".join(empty_terms) if isinstance(empty_terms, list) else ""
    empty_input = st.text_input(
        "空话套话（逗号分隔）",
        value=empty_str,
        placeholder="我觉得, 我认为, 非常重要",
        key=f"empty_terms_{domain_key}"
    )
    config['empty_phrases'] = {
        "description": "空话套话",
        "terms": [s.strip() for s in empty_input.split(',') if s.strip()]
    }


def render_config_editor():
    """渲染配置编辑器"""
    if st.session_state.domain_configs is None:
        st.info("👆 请先选择现有域或使用AI生成新配置")
        return
    
    configs = st.session_state.domain_configs
    
    # 显示当前编辑状态
    if st.session_state.is_editing_existing:
        st.info(f"📝 正在编辑域: **{st.session_state.current_domain_id}**")
    else:
        st.success(f"🆕 创建新域")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 基本信息", "🛠️ 技能体系", "❓ 问题模板", "🔍 评估信号"])
    
    with tab1:
        render_basic_info_tab(configs.get('domain_config', {}))
    
    with tab2:
        render_skills_tab(configs.get('skills_taxonomy', {}))
    
    with tab3:
        render_questions_tab(configs.get('question_templates', {}))
    
    with tab4:
        render_signals_tab(configs.get('assessment_signals', {}))
    
    st.markdown("---")
    
    # 保存按钮
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    
    with col1:
        if st.button("💾 保存配置", type="primary", use_container_width=True):
            domain_id = configs['domain_config'].get('domain_id', '')
            domain_name = configs['domain_config'].get('domain_name', '')
            
            if not domain_id or not domain_name:
                st.error("❌ 领域ID和名称不能为空")
            else:
                try:
                    generator = DomainConfigGenerator()
                    success = generator.save_domain_config(domain_id, configs)
                    if success:
                        st.success(f"✅ 配置已保存到: domains/{domain_id}/")
                        st.session_state.current_domain_id = domain_id
                        st.session_state.is_editing_existing = True
                except Exception as e:
                    st.error(f"❌ 保存失败: {str(e)}")
    
    with col2:
        if st.button("👀 预览JSON", use_container_width=True):
            with st.expander("查看完整JSON配置", expanded=True):
                st.json(configs)
    
    with col3:
        if st.button("🔄 重置", use_container_width=True):
            st.session_state.domain_configs = None
            st.session_state.current_domain_id = None
            st.rerun()


def main():
    initialize_session_state()
    
    st.title("⚙️ 域配置管理")
    st.markdown("创建和管理面试领域配置")
    st.markdown("---")
    
    # AI生成区域
    render_ai_generation_section()
    
    st.markdown("---")
    
    # 域选择器
    render_domain_selector()
    
    st.markdown("---")
    
    # 配置编辑器
    render_config_editor()


if __name__ == "__main__":
    main()
