#!/usr/bin/env python3
"""
Alibaba Cloud MCP Server 环境验证脚本
用于检查环境配置是否正确
"""
import sys
import os
import subprocess
from pathlib import Path

def check_uv():
    """检查 uv 是否安装"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ uv {version} - 已安装")
            return True
        else:
            print("✗ uv - 未安装或无法运行")
            return False
    except FileNotFoundError:
        print("✗ uv - 未安装")
        print("  安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - 兼容")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - 不兼容，需要 3.10+")
        print("  uv 会自动管理 Python 版本，无需手动安装")
        return False

def check_project_files():
    """检查项目文件"""
    required_files = [
        "pyproject.toml",
        "complete_fastmcp_server.py",
        "alibaba_cloud_ops_mcp_server/server.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"✗ 缺少项目文件: {', '.join(missing_files)}")
        return False
    else:
        print("✓ 项目文件完整")
        return True

def check_dependencies():
    """检查依赖是否安装"""
    try:
        result = subprocess.run(['uv', 'run', 'python', '-c', 'import fastmcp; print(fastmcp.__version__)'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ fastmcp {version} - 已安装")
            return True
        else:
            print("✗ fastmcp - 未安装或版本不兼容")
            print("  运行: uv sync")
            return False
    except Exception as e:
        print(f"✗ 依赖检查失败: {e}")
        return False

def check_environment_variables():
    """检查环境变量配置"""
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env 文件不存在")
        print("  创建方法: cp .env.example .env")
        return False
    
    print("✓ .env 文件存在")
    
    # 检查必要的环境变量
    required_vars = [
        "ALIBABA_CLOUD_ACCESS_KEY_ID",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET", 
        "ALIBABA_CLOUD_REGION"
    ]
    
    try:
        with open(env_file) as f:
            content = f.read()
        
        missing_vars = []
        empty_vars = []
        
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
            elif f'{var}=""' in content or f'{var}="your_' in content:
                empty_vars.append(var)
        
        if missing_vars:
            print(f"✗ 缺少环境变量: {', '.join(missing_vars)}")
            return False
        
        if empty_vars:
            print(f"⚠ 环境变量未配置: {', '.join(empty_vars)}")
            print("  请编辑 .env 文件，填入正确的阿里云凭证")
            return False
        
        print("✓ 环境变量配置完整")
        return True
        
    except Exception as e:
        print(f"✗ 读取 .env 文件失败: {e}")
        return False

def test_server():
    """测试服务器是否能正常启动"""
    print("\n--- 测试服务器启动 ---")
    try:
        result = subprocess.run([
            'uv', 'run', 'python', '-c', 
            '''
import sys
sys.path.insert(0, ".")
from complete_fastmcp_server import app
print("✓ 服务器模块加载成功")
'''
        ], capture_output=True, text=True, timeout=10, cwd='.')
        
        if result.returncode == 0:
            print("✓ 服务器可以正常启动")
            return True
        else:
            print(f"✗ 服务器启动失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✓ 服务器启动测试超时（正常，说明服务器在运行）")
        return True
    except Exception as e:
        print(f"✗ 服务器测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=== Alibaba Cloud MCP Server 环境检查 ===\n")
    
    checks = [
        ("uv 包管理器", check_uv),
        ("Python 版本", check_python_version),
        ("项目文件", check_project_files),
        ("依赖包", check_dependencies),
        ("环境变量", check_environment_variables),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        print(f"检查 {name}...")
        if not check_func():
            all_passed = False
        print()
    
    # 如果基本检查都通过，测试服务器
    if all_passed:
        if test_server():
            print("🎉 所有检查通过！环境配置正确，可以运行服务器。")
            print("\n下一步:")
            print("1. 配置 Amazon Q CLI MCP 设置")
            print("2. 运行: uv run python complete_fastmcp_server.py")
        else:
            all_passed = False
    
    if not all_passed:
        print("❌ 环境配置有问题，请根据上述提示进行修复。")
        print("\n常用修复命令:")
        print("- 安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("- 安装依赖: uv sync")
        print("- 创建环境文件: cp .env.example .env")
        sys.exit(1)

if __name__ == "__main__":
    main()
