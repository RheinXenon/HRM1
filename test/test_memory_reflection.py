"""
测试记忆系统和反思机制
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory_system import MemorySystem, EpisodicMemory, SemanticMemory, WorkingMemory
from core.reflection_system import ReflectionSystem
from core.llm_client import LLMClient
from datetime import datetime
from loguru import logger


def test_working_memory():
    """测试短期记忆"""
    logger.info("\n" + "="*60)
    logger.info("测试1: 短期记忆 (Working Memory)")
    logger.info("="*60)
    
    memory_system = MemorySystem(storage_dir="data/memory_test")
    
    # 创建短期记忆
    wm = memory_system.create_working_memory(
        session_id="test_001",
        candidate_profile={
            "name": "张三",
            "skills": {"Python": 8, "算法": 7},
            "level": "senior"
        }
    )
    
    # 添加对话
    wm.add_conversation("interviewer", "请介绍一下你的Python经验", type="question")
    wm.add_conversation("candidate", "我有5年Python开发经验...", type="answer")
    
    # 添加评估
    wm.add_evaluation({
        "score": 85,
        "feedback": "回答很好"
    })
    
    logger.success(f"✅ 短期记忆创建成功: {len(wm.conversation_history)} 条对话, {len(wm.current_evaluations)} 次评估")
    
    # 清空
    memory_system.clear_working_memory()
    logger.info("🗑️  短期记忆已清空")


def test_episodic_memory():
    """测试情节记忆"""
    logger.info("\n" + "="*60)
    logger.info("测试2: 情节记忆 (Episodic Memory)")
    logger.info("="*60)
    
    memory_system = MemorySystem(storage_dir="data/memory_test")
    
    # 创建情节记忆
    episode1 = EpisodicMemory(
        memory_id="ep_001",
        interview_id="interview_001",
        timestamp=datetime.now(),
        scenario_type="followup",
        question_category="技术能力",
        skill_area="Python",
        question="你提到了异步编程，能详细说说吗？",
        answer="嗯...这个我了解不是很深...",
        evaluation={"score": 45, "feedback": "追问后露怯"},
        strategy_used="followup",
        effectiveness=0.9,
        tags=["followup", "technical_depth"],
        is_successful=True,
        is_failure=False,
        lessons_learned="追问有效揭示了知识盲区"
    )
    
    episode2 = EpisodicMemory(
        memory_id="ep_002",
        interview_id="interview_002",
        timestamp=datetime.now(),
        scenario_type="normal",
        question_category="算法",
        skill_area="算法",
        question="请解释快速排序的原理",
        answer="快速排序采用分治策略，选择一个pivot...",
        evaluation={"score": 90, "feedback": "理解深刻"},
        strategy_used="direct",
        effectiveness=0.8,
        tags=["algorithm"],
        is_successful=True
    )
    
    # 添加到记忆系统
    memory_system.add_episodic_memory(episode1)
    memory_system.add_episodic_memory(episode2)
    
    logger.success(f"✅ 添加了 {len(memory_system.episodic_memories)} 个情节记忆")
    
    # 检索相关记忆
    results = memory_system.retrieve_episodic_memories(
        skill_area="Python",
        tags=["followup"],
        limit=5
    )
    
    logger.info(f"🔍 检索到 {len(results)} 个相关记忆:")
    for mem in results:
        logger.info(f"  - {mem.memory_id}: {mem.question[:30]}...")
    
    # 保存
    memory_system.save_memories()
    logger.success("💾 记忆已保存")


def test_semantic_memory():
    """测试语义记忆"""
    logger.info("\n" + "="*60)
    logger.info("测试3: 语义记忆 (Semantic Memory)")
    logger.info("="*60)
    
    memory_system = MemorySystem(storage_dir="data/memory_test")
    
    # 创建语义记忆
    semantic1 = SemanticMemory(
        memory_id="sem_001",
        knowledge_type="best_practice",
        pattern_name="追问策略有效性",
        pattern_description="当候选人使用高级术语但缺乏细节时，追问能有效揭示真实能力",
        applicable_conditions=["回答浮于表面", "使用专业术语但无具体示例"],
        usage_count=15,
        success_rate=0.85,
        confidence=0.75,
        supporting_examples=["ep_001", "ep_003", "ep_007"]
    )
    
    memory_system.add_semantic_memory(semantic1)
    
    # 更新统计
    semantic1.update_statistics(success=True)
    logger.info(f"📊 更新后: 使用{semantic1.usage_count}次, 成功率{semantic1.success_rate:.2%}")
    
    # 检索语义模式
    patterns = memory_system.retrieve_semantic_patterns(
        knowledge_type="best_practice",
        min_confidence=0.5
    )
    
    logger.success(f"✅ 检索到 {len(patterns)} 个语义模式")
    for pattern in patterns:
        logger.info(f"  - {pattern.pattern_name}: 成功率 {pattern.success_rate:.1%}, 置信度 {pattern.confidence:.1%}")


def test_memory_extraction():
    """测试从面试数据提取记忆"""
    logger.info("\n" + "="*60)
    logger.info("测试4: 从面试数据提取记忆")
    logger.info("="*60)
    
    memory_system = MemorySystem(storage_dir="data/memory_test")
    
    # 模拟面试数据
    interview_data = {
        "interview_id": "test_interview_001",
        "conversation_log": [
            {"role": "interviewer", "content": "请介绍你的项目经验", "category": "职位相关"},
            {"role": "candidate", "content": "我参与过多个大型项目..."},
            {"role": "system", "content": "标准化评分: 75.0/100, 建议: 良好"},
            {"role": "interviewer", "content": "你提到了微服务，能详细说说吗？", "type": "followup", "category": "技术能力"},
            {"role": "candidate", "content": "嗯...微服务就是...这个..."},
            {"role": "system", "content": "追问评分: 45.0/100, 🚩 追问后露怯"}
        ]
    }
    
    # 提取情节
    episodes = memory_system.extract_episodes_from_interview(interview_data)
    
    logger.success(f"✅ 提取了 {len(episodes)} 个情节记忆")
    for ep in episodes:
        logger.info(f"  - {ep.scenario_type}: {ep.question[:40]}...")


def test_immediate_reflection():
    """测试即时反思"""
    logger.info("\n" + "="*60)
    logger.info("测试5: 即时反思 (Immediate Reflection)")
    logger.info("="*60)
    
    llm_client = LLMClient()
    reflection_system = ReflectionSystem(llm_client, storage_dir="data/reflections_test")
    
    # 模拟面试数据
    interview_data = {
        "interview_id": "test_001",
        "conversation_log": [
            {"role": "interviewer", "content": "问题1", "category": "技术"},
            {"role": "candidate", "content": "回答1"},
            {"role": "system", "content": "标准化评分: 80.0/100, 建议: 良好"},
            {"role": "interviewer", "content": "追问1", "type": "followup"},
            {"role": "candidate", "content": "追问回答"},
            {"role": "system", "content": "追问评分: 50.0/100, 🚩 追问后露怯"}
        ],
        "evaluation": {"recommendation_score": 65},
        "duration_seconds": 1200
    }
    
    # 执行即时反思
    reflection = reflection_system.immediate_reflection(interview_data)
    
    logger.success(f"✅ 即时反思完成")
    logger.info(f"  - 发现: {len(reflection.findings)} 项")
    logger.info(f"  - 洞察: {len(reflection.insights)} 条")
    logger.info(f"  - 建议: {len(reflection.improvement_suggestions)} 条")
    
    # 打印反思报告
    report = reflection_system.generate_reflection_report(reflection)
    print("\n" + report)
    
    reflection_system.save_all()


def test_periodic_reflection():
    """测试阶段性反思"""
    logger.info("\n" + "="*60)
    logger.info("测试6: 阶段性反思 (Periodic Reflection)")
    logger.info("="*60)
    
    llm_client = LLMClient()
    reflection_system = ReflectionSystem(llm_client, storage_dir="data/reflections_test")
    
    # 模拟多次面试数据
    interview_batch = []
    for i in range(5):
        interview_batch.append({
            "interview_id": f"test_{i:03d}",
            "conversation_log": [
                {"role": "interviewer", "content": f"问题{i}"},
                {"role": "candidate", "content": f"回答{i}"},
                {"role": "system", "content": f"评分: {60 + i*5}"}
            ],
            "evaluation": {"recommendation_score": 60 + i*5},
            "duration_seconds": 1000 + i*100
        })
    
    # 执行阶段性反思
    reflection = reflection_system.periodic_reflection(interview_batch, batch_size=5)
    
    logger.success(f"✅ 阶段性反思完成")
    logger.info(f"  - 分析了 {len(interview_batch)} 次面试")
    logger.info(f"  - 发现: {len(reflection.findings)} 项")
    logger.info(f"  - 建议: {len(reflection.improvement_suggestions)} 条")
    
    reflection_system.save_all()


def test_integration():
    """集成测试：完整流程"""
    logger.info("\n" + "="*60)
    logger.info("测试7: 集成测试")
    logger.info("="*60)
    
    from core.interview_engine import InterviewEngine
    from config import load_candidate_template
    
    # 创建启用记忆和反思的面试引擎
    engine = InterviewEngine(enable_memory=True, enable_reflection=True)
    
    logger.info("✅ 面试引擎已创建（启用记忆和反思）")
    logger.info(f"  - 记忆系统: {'启用' if engine.memory_system else '禁用'}")
    logger.info(f"  - 反思机制: {'启用' if engine.reflection_system else '禁用'}")
    
    # 可以在这里运行一次完整面试测试（如果需要）
    # ideal_candidate = load_candidate_template('ideal_candidate')
    # result = engine.run_interview(ideal_candidate, mode="demo")


def run_all_tests():
    """运行所有测试"""
    logger.info("\n" + "🧪"*30)
    logger.info("开始测试记忆系统和反思机制")
    logger.info("🧪"*30)
    
    try:
        test_working_memory()
        test_episodic_memory()
        test_semantic_memory()
        test_memory_extraction()
        test_immediate_reflection()
        test_periodic_reflection()
        test_integration()
        
        logger.info("\n" + "="*60)
        logger.success("✅ 所有测试通过!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    run_all_tests()
