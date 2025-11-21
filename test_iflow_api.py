"""
测试 iflow API 连接
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.llm_client import LLMClient
from loguru import logger

def test_iflow_connection():
    """测试iflow API连接"""
    print("=" * 60)
    print("🧪 测试 iflow API 连接")
    print("=" * 60)
    
    try:
        # 初始化客户端
        client = LLMClient()
        print(f"\n✅ LLM客户端初始化成功")
        print(f"   API URL: {client.base_url}")
        print(f"   Model: {client.model}")
        print(f"   API Key: {client.api_key[:20]}...")
        
        # 测试简单对话
        print("\n🚀 测试API调用...")
        response = client.chat_with_system_prompt(
            system_prompt="你是一个友好的AI助手。",
            user_message="请用一句话介绍你自己。",
            temperature=0.7
        )
        
        print(f"\n✅ API调用成功！")
        print(f"📝 模型回复: {response}")
        
        # 测试JSON响应
        print("\n🚀 测试JSON格式响应...")
        messages = [
            {"role": "system", "content": "你是一个数据助手，总是返回JSON格式。"},
            {"role": "user", "content": '请返回一个包含name和age的JSON对象，name为"测试"，age为25。'}
        ]
        
        json_response = client.chat_with_json_response(messages, temperature=0.3)
        print(f"✅ JSON响应成功！")
        print(f"📊 返回数据: {json_response}")
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！iflow API配置正确")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("💡 检查清单:")
        print("1. 确认.env文件中的QWEN_API_KEY配置正确")
        print("2. 确认QWEN_API_URL为: https://apis.iflow.cn/v1")
        print("3. 确认QWEN_MODEL为: qwen3-max")
        print("4. 确认网络连接正常")
        print("=" * 60)
        
        return False


if __name__ == "__main__":
    test_iflow_connection()
