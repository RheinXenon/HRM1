"""
反思工具
提供阶段性反思和深度反思的工具函数
"""

from typing import List, Dict
from pathlib import Path
import json
from loguru import logger
from datetime import datetime

from core.reflection_system import ReflectionSystem
from core.llm_client import LLMClient


def load_recent_interviews(limit: int = 10) -> List[Dict]:
    """
    加载最近的面试记录
    
    Args:
        limit: 加载数量限制
        
    Returns:
        面试记录列表
    """
    interviews_dir = Path("data/interviews")
    if not interviews_dir.exists():
        logger.warning("未找到面试记录目录")
        return []
    
    # 获取所有JSON文件并按时间排序
    interview_files = sorted(
        interviews_dir.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    interviews = []
    for filepath in interview_files[:limit]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                interviews.append(data)
        except Exception as e:
            logger.error(f"加载面试记录失败 {filepath}: {e}")
    
    logger.info(f"✅ 加载了 {len(interviews)} 条面试记录")
    return interviews


def load_all_interviews() -> List[Dict]:
    """
    加载所有面试记录
    
    Returns:
        所有面试记录列表
    """
    interviews_dir = Path("data/interviews")
    if not interviews_dir.exists():
        logger.warning("未找到面试记录目录")
        return []
    
    interviews = []
    for filepath in interviews_dir.glob("*.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                interviews.append(data)
        except Exception as e:
            logger.error(f"加载面试记录失败 {filepath}: {e}")
    
    logger.info(f"✅ 加载了 {len(interviews)} 条面试记录")
    return interviews


def run_periodic_reflection(batch_size: int = 10, save_report: bool = True):
    """
    运行阶段性反思
    
    Args:
        batch_size: 批次大小
        save_report: 是否保存报告到文件
    """
    logger.info("="*60)
    logger.info("📊 开始阶段性反思")
    logger.info("="*60)
    
    # 加载最近的面试
    interviews = load_recent_interviews(limit=batch_size)
    
    if not interviews:
        logger.warning("没有可用的面试记录")
        return None
    
    # 创建反思系统
    llm_client = LLMClient()
    reflection_system = ReflectionSystem(llm_client)
    
    # 执行阶段性反思
    reflection = reflection_system.periodic_reflection(interviews, batch_size)
    
    # 生成报告
    report = reflection_system.generate_reflection_report(reflection)
    print("\n" + report)
    
    # 保存报告到文件
    if save_report:
        report_dir = Path("data/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"periodic_reflection_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.success(f"📄 报告已保存: {report_file}")
    
    # 保存反思数据
    reflection_system.save_all()
    
    return reflection


def run_deep_reflection(save_report: bool = True):
    """
    运行深度反思
    
    Args:
        save_report: 是否保存报告到文件
    """
    logger.info("="*60)
    logger.info("🧐 开始深度反思")
    logger.info("="*60)
    
    # 加载所有面试
    interviews = load_all_interviews()
    
    if not interviews:
        logger.warning("没有可用的面试记录")
        return None
    
    # 创建反思系统
    llm_client = LLMClient()
    reflection_system = ReflectionSystem(llm_client)
    
    # 执行深度反思
    reflection = reflection_system.deep_reflection(interviews)
    
    # 生成报告
    report = reflection_system.generate_reflection_report(reflection)
    print("\n" + report)
    
    # 保存报告到文件
    if save_report:
        report_dir = Path("data/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"deep_reflection_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.success(f"📄 报告已保存: {report_file}")
    
    # 保存反思数据
    reflection_system.save_all()
    
    return reflection


def view_reflection_statistics():
    """
    查看反思统计信息
    """
    reflection_system = ReflectionSystem(LLMClient())
    
    stats = reflection_system.stats
    
    print("\n" + "="*60)
    print("📊 反思系统统计")
    print("="*60)
    print(f"总反思次数: {stats['total_reflections']}")
    print(f"  - 即时反思: {stats['immediate_reflections']}")
    print(f"  - 阶段性反思: {stats['periodic_reflections']}")
    print(f"  - 深度反思: {stats['deep_reflections']}")
    print(f"\n改进建议数: {stats['improvements_suggested']}")
    print(f"已应用改进: {stats['improvements_applied']}")
    print("="*60)


def view_memory_statistics():
    """
    查看记忆系统统计信息
    """
    from core.memory_system import MemorySystem
    
    memory_system = MemorySystem()
    
    print("\n" + "="*60)
    print("💭 记忆系统统计")
    print("="*60)
    print(f"情节记忆数: {len(memory_system.episodic_memories)}")
    print(f"语义记忆数: {len(memory_system.semantic_memories)}")
    
    # 统计情节记忆的类型
    if memory_system.episodic_memories:
        scenario_types = {}
        for episode in memory_system.episodic_memories:
            scenario_types[episode.scenario_type] = scenario_types.get(episode.scenario_type, 0) + 1
        
        print(f"\n情节类型分布:")
        for scenario, count in scenario_types.items():
            print(f"  - {scenario}: {count}")
    
    # 显示语义记忆
    if memory_system.semantic_memories:
        print(f"\n语义记忆列表:")
        for i, (mem_id, semantic) in enumerate(memory_system.semantic_memories.items(), 1):
            print(f"  {i}. {semantic.pattern_name}")
            print(f"     使用次数: {semantic.usage_count}, 成功率: {semantic.success_rate:.1%}, 置信度: {semantic.confidence:.1%}")
    
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python reflection_tools.py periodic [batch_size]  # 阶段性反思")
        print("  python reflection_tools.py deep                   # 深度反思")
        print("  python reflection_tools.py stats                  # 查看统计")
        print("  python reflection_tools.py memory                 # 查看记忆统计")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "periodic":
        batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        run_periodic_reflection(batch_size=batch_size)
    
    elif command == "deep":
        run_deep_reflection()
    
    elif command == "stats":
        view_reflection_statistics()
    
    elif command == "memory":
        view_memory_statistics()
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
