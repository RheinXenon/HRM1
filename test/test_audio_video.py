"""
音视频功能测试脚本
用于验证音视频依赖和设备是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.audio_video_tools import check_dependencies

def test_dependencies():
    """测试依赖检查功能"""
    print("=" * 60)
    print("音视频功能测试")
    print("=" * 60)
    print()
    
    # 测试1: 仅检查库（不访问硬件）
    print("【测试1】检查库安装（不访问硬件）")
    print("-" * 60)
    status = check_dependencies(check_hardware=False)
    
    print(f"语音识别库: {'✅ 已安装' if status['speech_recognition'] else '❌ 未安装'}")
    print(f"OpenCV库: {'✅ 已安装' if status['opencv'] else '❌ 未安装'}")
    print(f"麦克风功能: {'✅ 就绪' if status['microphone'] else '❌ 不可用'}")
    print(f"摄像头功能: {'✅ 就绪' if status['camera'] else '❌ 不可用'}")
    print()
    
    # 测试2: 检查硬件设备（可能会访问设备）
    print("【测试2】检查硬件设备（会尝试访问麦克风和摄像头）")
    print("-" * 60)
    print("警告：这可能会触发系统权限请求")
    input("按回车键继续...")
    
    try:
        status_hw = check_dependencies(check_hardware=True)
        print(f"麦克风实际状态: {'✅ 可用' if status_hw['microphone'] else '❌ 不可用'}")
        print(f"摄像头实际状态: {'✅ 可用' if status_hw['camera'] else '❌ 不可用'}")
    except Exception as e:
        print(f"❌ 硬件检查失败: {e}")
    print()
    
    # 建议
    print("=" * 60)
    print("📋 安装建议")
    print("=" * 60)
    
    if not status['speech_recognition']:
        print("⚠️ 语音识别库未安装")
        print("   安装命令：pip install SpeechRecognition pyaudio")
        print("   Windows用户可能需要：conda install pyaudio")
        print()
    
    if not status['opencv']:
        print("⚠️ OpenCV库未安装")
        print("   安装命令：pip install opencv-python")
        print()
    
    if status['speech_recognition'] and status['opencv']:
        print("✅ 所有依赖已安装！")
        print("💡 如果设备功能不可用，请检查：")
        print("   - 设备是否连接")
        print("   - 系统权限设置")
        print("   - 是否被其他程序占用")
    
    print("=" * 60)


if __name__ == "__main__":
    test_dependencies()
