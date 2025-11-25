"""
测试脚本：验证候选人在知识盲区中的真实回答表现
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# 将项目根目录加入路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import load_candidate_template  # noqa: E402
from core import InterviewEngine  # noqa: E402


def format_area(area: Dict[str, Any]) -> str:
    """格式化知识盲区条目"""
    skill = area.get("skill", "未知技能")
    actual = area.get("actual_level", 0)
    perceived = area.get("perceived_level", 0)
    gap = perceived - actual
    return f"- {skill}: 实际{actual}/10，自我感觉{perceived}/10 (差值 +{gap})"


def find_skill_mentions(conversation: List[Dict[str, Any]], skill: str) -> List[Dict[str, Any]]:
    """在对话中查找包含指定技能名称的消息"""
    mentions = []
    keyword = skill.lower()
    for idx, entry in enumerate(conversation):
        content = entry.get("content", "")
        if not isinstance(content, str):
            continue
        if keyword in content.lower():
            mentions.append({
                "index": idx,
                "role": entry.get("role", "unknown"),
                "type": entry.get("type", ""),
                "content": content.strip()
            })
    return mentions


def extract_followup_flags(conversation: List[Dict[str, Any]]) -> List[str]:
    """提取系统标记为追问后露怯的内容"""
    flags = []
    for entry in conversation:
        content = entry.get("content", "")
        if isinstance(content, str) and "追问后露怯" in content:
            flags.append(content.strip())
    return flags


def run_blind_spot_test():
    print("\n" + "=" * 80)
    print("🧪 知识盲区表现测试")
    print("=" * 80)

    candidate_config = load_candidate_template("overconfident_candidate")
    profile = candidate_config["profile"]
    blind_spots = profile.get("knowledge_blind_spots") or {}

    print(f"候选人: {profile.get('name', '未知')}\n")

    overconfident_areas = blind_spots.get("overconfident_areas", [])
    if not overconfident_areas:
        print("⚠️  此候选人未配置过度自信盲区，无法测试。")
        return

    print("🔴 过度自信领域:")
    for area in overconfident_areas:
        print("   " + format_area(area))

    print("\n🚀 开始运行面试 (demo 模式)...\n")
    engine = InterviewEngine()
    result = engine.run_interview(
        job_file="senior_backend",
        company_file="tech_startup",
        candidate_config=candidate_config,
        mode="demo"
    )

    conversation = result.conversation_log

    print("\n" + "=" * 80)
    print("📊 盲区命中分析")
    print("=" * 80)

    for area in overconfident_areas:
        skill = area.get("skill", "")
        print(f"\n🔍 技能: {skill}")
        mentions = find_skill_mentions(conversation, skill)
        if not mentions:
            print("   ⚠️  本轮对话中未触及该技能。")
            continue
        for item in mentions:
            role = item["role"]
            entry_type = item["type"] or "normal"
            content_preview = item["content"].replace("\n", " ")
            print(f"   [#{item['index']}] {role} ({entry_type}): {content_preview[:220]}")

    flags = extract_followup_flags(conversation)
    print("\n" + "=" * 80)
    print("🚩 追问标记")
    print("=" * 80)
    if flags:
        for flag in flags:
            print(f"- {flag}")
    else:
        print("暂无 '追问后露怯' 标记，可考虑重新运行或调整候选人配置。")

    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    run_blind_spot_test()
