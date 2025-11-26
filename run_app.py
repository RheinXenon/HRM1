"""
HRM1 智能面试系统 - 启动脚本
自动启动Streamlit应用并在浏览器中打开
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path
import socket


def find_free_port(start_port=8501, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port


def main():
    """启动应用"""
    print("=" * 60)
    print("🎯 HRM1 智能面试系统")
    print("=" * 60)
    print()
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    app_file = current_dir / "app.py"
    
    if not app_file.exists():
        print("❌ 错误: 找不到 app.py 文件")
        input("按任意键退出...")
        sys.exit(1)
    
    # 查找可用端口
    port = find_free_port()
    print(f"📡 使用端口: {port}")
    print()
    
    # 构建streamlit命令
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("🚀 正在启动 Streamlit 服务器...")
    print()
    
    try:
        # 启动streamlit进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 等待服务器启动
        url = f"http://localhost:{port}"
        max_wait = 15
        waited = 0
        
        print("⏳ 等待服务器启动...", end="", flush=True)
        
        while waited < max_wait:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    print(" ✅")
                    break
            except:
                pass
            
            time.sleep(0.5)
            waited += 0.5
            print(".", end="", flush=True)
        
        if waited >= max_wait:
            print("\n⚠️  服务器启动超时，但仍会尝试打开浏览器")
        
        print()
        print("=" * 60)
        print(f"✅ 应用已启动！")
        print(f"🌐 访问地址: {url}")
        print("=" * 60)
        print()
        print("💡 提示:")
        print("  - 浏览器将自动打开应用页面")
        print("  - 按 Ctrl+C 停止服务器")
        print("  - 关闭此窗口也会停止服务器")
        print()
        
        # 打开浏览器
        time.sleep(1)
        webbrowser.open(url)
        
        # 保持进程运行并输出日志
        print("=" * 60)
        print("📋 服务器日志:")
        print("=" * 60)
        
        for line in process.stdout:
            print(line, end="")
        
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务器...")
        process.terminate()
        process.wait()
        print("✅ 服务器已停止")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请尝试手动运行:")
        print(f"  streamlit run app.py --server.port {port}")
        input("\n按任意键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
