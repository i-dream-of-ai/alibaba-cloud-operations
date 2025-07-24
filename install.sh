#!/bin/bash
set -e

echo "=== Alibaba Cloud MCP Server 安装脚本 ==="
echo

# 检查是否安装了 uv
if ! command -v uv &> /dev/null; then
    echo "📦 安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc || source ~/.zshrc || true
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✓ uv 已安装"
fi

# 检查 uv 版本
echo "📋 uv 版本: $(uv --version)"

# 同步依赖
echo "📦 安装项目依赖..."
uv sync

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 创建 .env 文件..."
        cp .env.example .env
        echo "⚠️  请编辑 .env 文件，填入你的阿里云凭证"
    else
        echo "📝 创建 .env 文件..."
        cat > .env << 'EOF'
# 阿里云访问凭证
ALIBABA_CLOUD_ACCESS_KEY_ID="your_access_key_id_here"
ALIBABA_CLOUD_ACCESS_KEY_SECRET="your_access_key_secret_here"
ALIBABA_CLOUD_REGION="cn-beijing"
FASTMCP_LOG_LEVEL="INFO"
EOF
        echo "⚠️  请编辑 .env 文件，填入你的阿里云凭证"
    fi
else
    echo "✓ .env 文件已存在"
fi

# 运行验证脚本
echo
echo "🔍 运行环境验证..."
if uv run python verify_setup.py; then
    echo
    echo "🎉 安装完成！"
    echo
    echo "下一步配置 Amazon Q CLI:"
    echo "1. 编辑 ~/.aws/amazonq/mcp.json"
    echo "2. 添加以下配置:"
    echo
    echo '{
  "mcpServers": {
    "alibaba-cloud-ops-mcp-server": {
      "timeout": 30000,
      "command": "uv",
      "args": [
        "--directory",
        "'$(pwd)'",
        "run",
        "python",
        "complete_fastmcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}'
    echo
    echo "3. 重启 Amazon Q CLI"
    echo
    echo "测试服务器: uv run python complete_fastmcp_server.py"
else
    echo "❌ 安装验证失败，请检查错误信息"
    exit 1
fi
