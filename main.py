"""
主入口文件 - 快速启动示例
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import load_candidate_template, load_job_config, load_company_config


def quick_demo():
    """快速演示示例"""
    print("=" * 60)
    print("自动面试系统 - 快速演示")
    print("=" * 60)
    print()
    
    # 加载配置
    print("📋 加载配置文件...")
    try:
        candidate = load_candidate_template("ideal_candidate")
        job = load_job_config("senior_backend")
        company = load_company_config("tech_startup")
        
        print(f"✅ 候选人: {candidate['profile']['name']}")
        print(f"✅ 职位: {job['title']}")
        print(f"✅ 公司: {company['name']}")
        print()
        
        # TODO: 这里将来会调用面试引擎
        print("⚠️  面试引擎尚未实现，请等待后续开发...")
        print()
        print("候选人技能概览:")
        for skill, level in candidate['profile']['skills'].items():
            print(f"  - {skill}: {level}/10")
        
    except FileNotFoundError as e:
        print(f"❌ 配置文件加载失败: {e}")
        return
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return
    
    print()
    print("=" * 60)
    print("演示完成！")
    print("下一步: 实现面试引擎核心逻辑")
    print("=" * 60)


if __name__ == "__main__":
    quick_demo()
