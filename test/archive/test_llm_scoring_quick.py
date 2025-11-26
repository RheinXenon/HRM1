"""
快速LLM评分测试 - 仅测试一个场景
用于快速验证LLM评分是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test_llm_scoring import LLMScoringTester
from loguru import logger


def main():
    """快速测试一个场景"""
    print("\n" + "="*80)
    print("🚀 快速LLM评分测试")
    print("="*80)
    print("仅测试一个优秀候选人场景，验证系统是否正常工作")
    print("="*80)
    
    tester = LLMScoringTester()
    
    try:
        result = tester.test_excellent_candidate()
        
        print("\n" + "="*80)
        if result.get("status") == "PASS":
            print("🎉 测试通过! LLM评分系统工作正常")
            return 0
        elif result.get("status") == "WARNING":
            print("⚠️  测试有警告，但基本功能正常")
            print("   可能需要调整预期范围或检查LLM评分逻辑")
            return 0
        else:
            print("❌ 测试失败")
            return 1
            
    except Exception as e:
        logger.error(f"❌ 测试执行失败: {e}")
        print("\n可能的原因:")
        print("1. API密钥未配置或无效")
        print("2. 网络连接问题")
        print("3. API额度不足")
        print("\n请检查 .env 文件中的配置:")
        print("  QWEN_API_KEY=your_api_key")
        print("  QWEN_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
