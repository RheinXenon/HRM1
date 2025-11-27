"""
记忆与反思系统页面
展示Agent的记忆积累和反思分析结果
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_system import MemorySystem
from core.reflection_system import ReflectionSystem
from core.llm_client import LLMClient
from core.reflection_tools import load_recent_interviews, load_all_interviews

# 页面配置
st.set_page_config(
    page_title="记忆与反思 - HRM1",
    page_icon="🧠",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    .memory-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .reflection-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .episode-item {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .semantic-item {
        background: #f0fdf4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
    }
    .finding-box {
        background: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 0.5rem 0;
    }
    .suggestion-box {
        background: #e0e7ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #6366f1;
        margin: 0.5rem 0;
    }
    .stat-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.title("🧠 Agent记忆与反思系统")
st.markdown("---")

# 初始化系统
@st.cache_resource
def init_systems():
    """初始化记忆和反思系统"""
    memory_system = MemorySystem()
    llm_client = LLMClient()
    reflection_system = ReflectionSystem(llm_client)
    return memory_system, reflection_system

memory_system, reflection_system = init_systems()

# 选项卡
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 系统概览",
    "💭 记忆系统", 
    "🤔 反思分析",
    "🔧 管理工具"
])

# ==================== Tab 1: 系统概览 ====================
with tab1:
    st.header("📊 系统概览")
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(memory_system.episodic_memories)}</div>
            <p>情节记忆</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(memory_system.semantic_memories)}</div>
            <p>语义记忆</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{reflection_system.stats['total_reflections']}</div>
            <p>总反思次数</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{reflection_system.stats['improvements_suggested']}</div>
            <p>改进建议数</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 记忆分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💭 情节记忆分布")
        if memory_system.episodic_memories:
            # 按场景类型统计
            scenario_counts = {}
            for ep in memory_system.episodic_memories:
                scenario_counts[ep.scenario_type] = scenario_counts.get(ep.scenario_type, 0) + 1
            
            df = pd.DataFrame([
                {"场景类型": k, "数量": v}
                for k, v in scenario_counts.items()
            ])
            st.bar_chart(df.set_index("场景类型"))
        else:
            st.info("暂无情节记忆")
    
    with col2:
        st.subheader("🤔 反思统计")
        if reflection_system.stats['total_reflections'] > 0:
            df = pd.DataFrame([
                {"类型": "即时反思", "数量": reflection_system.stats['immediate_reflections']},
                {"类型": "阶段性反思", "数量": reflection_system.stats['periodic_reflections']},
                {"类型": "深度反思", "数量": reflection_system.stats['deep_reflections']},
            ])
            st.bar_chart(df.set_index("类型"))
        else:
            st.info("暂无反思记录")

# ==================== Tab 2: 记忆系统 ====================
with tab2:
    st.header("💭 记忆系统")
    
    # 子选项卡
    sub_tab1, sub_tab2 = st.tabs(["情节记忆", "语义记忆"])
    
    # 情节记忆
    with sub_tab1:
        st.subheader("📚 情节记忆列表")
        
        # 筛选选项
        col1, col2, col3 = st.columns(3)
        with col1:
            skill_filter = st.selectbox(
                "技能领域",
                ["全部"] + list(set(ep.skill_area for ep in memory_system.episodic_memories))
            )
        with col2:
            scenario_filter = st.selectbox(
                "场景类型",
                ["全部"] + list(set(ep.scenario_type for ep in memory_system.episodic_memories))
            )
        with col3:
            only_successful = st.checkbox("只显示成功案例")
        
        # 检索记忆
        episodes = memory_system.retrieve_episodic_memories(
            skill_area=None if skill_filter == "全部" else skill_filter,
            scenario_type=None if scenario_filter == "全部" else scenario_filter,
            only_successful=only_successful,
            limit=50
        )
        
        st.write(f"找到 {len(episodes)} 条记忆")
        
        # 显示记忆
        for i, ep in enumerate(episodes, 1):
            with st.expander(f"记忆 {i}: {ep.skill_area} - {ep.scenario_type}"):
                st.markdown(f"""
                <div class="episode-item">
                    <strong>📋 面试ID:</strong> {ep.interview_id}<br>
                    <strong>🕐 时间:</strong> {ep.timestamp.strftime('%Y-%m-%d %H:%M')}<br>
                    <strong>📌 场景:</strong> {ep.scenario_type}<br>
                    <strong>💡 技能:</strong> {ep.skill_area}<br>
                    <strong>✨ 效果:</strong> {ep.effectiveness * 100:.0f}%<br>
                    <strong>🏷️ 标签:</strong> {', '.join(ep.tags)}<br>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("**❓ 问题:**")
                st.info(ep.question)
                
                st.write("**💬 回答:**")
                st.success(ep.answer)
                
                st.write("**📊 评估:**")
                st.json(ep.evaluation)
                
                if ep.lessons_learned:
                    st.write("**📖 经验总结:**")
                    st.warning(ep.lessons_learned)
    
    # 语义记忆
    with sub_tab2:
        st.subheader("🧩 语义记忆 - 提炼的模式和规律")
        
        if memory_system.semantic_memories:
            for mem_id, semantic in memory_system.semantic_memories.items():
                with st.expander(f"📊 {semantic.pattern_name}"):
                    st.markdown(f"""
                    <div class="semantic-item">
                        <strong>📝 描述:</strong> {semantic.pattern_description}<br>
                        <strong>📈 使用次数:</strong> {semantic.usage_count}<br>
                        <strong>✅ 成功率:</strong> {semantic.success_rate * 100:.1f}%<br>
                        <strong>🎯 置信度:</strong> {semantic.confidence * 100:.1f}%<br>
                        <strong>🔄 更新时间:</strong> {semantic.last_updated.strftime('%Y-%m-%d %H:%M')}<br>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if semantic.applicable_conditions:
                        st.write("**📋 适用条件:**")
                        for cond in semantic.applicable_conditions:
                            st.markdown(f"- {cond}")
                    
                    if semantic.supporting_examples:
                        st.write(f"**🔗 支持案例:** {len(semantic.supporting_examples)} 个")
        else:
            st.info("暂无语义记忆。系统会自动从情节记忆中提炼模式。")

# ==================== Tab 3: 反思分析 ====================
with tab3:
    st.header("🤔 反思分析")
    
    # 显示最近的反思
    if reflection_system.reflection_history:
        st.subheader("📜 反思历史")
        
        # 按时间排序
        sorted_reflections = sorted(
            reflection_system.reflection_history,
            key=lambda r: r.timestamp,
            reverse=True
        )
        
        for i, reflection in enumerate(sorted_reflections[:10], 1):
            level_emoji = {
                "immediate": "⚡",
                "periodic": "📊",
                "deep": "🧐"
            }
            
            level_name = {
                "immediate": "即时反思",
                "periodic": "阶段性反思",
                "deep": "深度反思"
            }
            
            with st.expander(
                f"{level_emoji.get(reflection.reflection_level, '🤔')} "
                f"{level_name.get(reflection.reflection_level, '反思')} - "
                f"{reflection.timestamp.strftime('%Y-%m-%d %H:%M')}"
            ):
                st.markdown(f"""
                <div class="reflection-card">
                    <strong>🆔 ID:</strong> {reflection.reflection_id}<br>
                    <strong>📊 关注领域:</strong> {', '.join(reflection.focus_areas)}<br>
                    <strong>🎯 置信度:</strong> {reflection.confidence * 100:.0f}%<br>
                </div>
                """, unsafe_allow_html=True)
                
                # 发现
                st.write(f"**🔍 发现 ({len(reflection.findings)} 项):**")
                for finding in reflection.findings:
                    finding_type = finding.get('type', 'neutral')
                    icon = "✅" if finding_type == "positive" else "⚠️" if finding_type == "concern" else "ℹ️"
                    
                    st.markdown(f"""
                    <div class="finding-box">
                        {icon} <strong>{finding.get('dimension')}:</strong><br>
                        {finding.get('details', '')}
                    </div>
                    """, unsafe_allow_html=True)
                
                # 洞察
                if reflection.insights:
                    st.write(f"**💡 洞察 ({len(reflection.insights)} 条):**")
                    for insight in reflection.insights:
                        st.info(insight)
                
                # 改进建议
                if reflection.improvement_suggestions:
                    st.write(f"**🎯 改进建议 ({len(reflection.improvement_suggestions)} 条):**")
                    for sugg in reflection.improvement_suggestions:
                        priority = sugg.get('priority', 'medium').upper()
                        priority_color = {
                            'CRITICAL': '🔴',
                            'HIGH': '🟠',
                            'MEDIUM': '🟡',
                            'LOW': '🟢'
                        }
                        
                        st.markdown(f"""
                        <div class="suggestion-box">
                            {priority_color.get(priority, '⚪')} <strong>[{priority}]</strong><br>
                            <strong>维度:</strong> {sugg.get('dimension')}<br>
                            <strong>行动:</strong> {sugg.get('action')}<br>
                            <strong>预期影响:</strong> {sugg.get('expected_impact', '未知')}
                        </div>
                        """, unsafe_allow_html=True)
                
                # 优先行动项
                if reflection.priority_actions:
                    st.write("**⚡ 优先行动项:**")
                    for action in reflection.priority_actions:
                        st.warning(f"▶️ {action}")
    else:
        st.info("暂无反思记录。运行面试后会自动生成即时反思。")

# ==================== Tab 4: 管理工具 ====================
with tab4:
    st.header("🔧 管理工具")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 运行阶段性反思")
        st.write("分析最近的面试，识别重复问题和改进机会")
        
        batch_size = st.number_input("分析面试数量", min_value=5, max_value=50, value=10)
        
        if st.button("🚀 运行阶段性反思", type="primary"):
            with st.spinner("正在进行阶段性反思分析..."):
                try:
                    from core.reflection_tools import run_periodic_reflection
                    reflection = run_periodic_reflection(batch_size=batch_size, save_report=True)
                    st.success("✅ 阶段性反思完成！")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 反思失败: {e}")
    
    with col2:
        st.subheader("🧐 运行深度反思")
        st.write("系统性分析所有历史面试，识别系统性问题")
        
        st.warning("⚠️ 深度反思需要分析所有面试记录，建议积累30+次面试后运行")
        
        if st.button("🔍 运行深度反思", type="secondary"):
            with st.spinner("正在进行深度反思分析（可能需要较长时间）..."):
                try:
                    from core.reflection_tools import run_deep_reflection
                    reflection = run_deep_reflection(save_report=True)
                    st.success("✅ 深度反思完成！")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 反思失败: {e}")
    
    st.markdown("---")
    
    # 数据管理
    st.subheader("💾 数据管理")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 刷新记忆索引"):
            memory_system._rebuild_index()
            st.success("✅ 索引已重建")
    
    with col2:
        if st.button("💾 保存记忆数据"):
            memory_system.save_memories()
            st.success("✅ 记忆已保存")
    
    with col3:
        if st.button("💾 保存反思数据"):
            reflection_system.save_all()
            st.success("✅ 反思数据已保存")
    
    st.markdown("---")
    
    # 统计信息
    st.subheader("📈 详细统计")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**💭 记忆系统统计:**")
        st.json({
            "情节记忆数": len(memory_system.episodic_memories),
            "语义记忆数": len(memory_system.semantic_memories),
            "索引数": len(memory_system.episodic_index)
        })
    
    with col2:
        st.write("**🤔 反思系统统计:**")
        st.json(reflection_system.stats)

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p>💡 <strong>提示:</strong> Agent会在每次面试后自动提取记忆和进行即时反思</p>
    <p>建议定期运行阶段性反思（10-20次面试后）和深度反思（30+次面试后）</p>
</div>
""", unsafe_allow_html=True)
