# Alibaba Cloud Operations MCP Server

一个用于 Amazon Q CLI 的阿里云操作 MCP 服务器，支持 ECS、VPC、RDS、OSS、CloudMonitor、OOS 等服务。

[English](README_EN.md) | 中文

## 系统要求

- Python 3.10+ (通过 uv 自动管理)
- [uv](https://docs.astral.sh/uv/) - Python 包和项目管理器
- 阿里云访问凭证

## 快速开始

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者使用 pip
pip install uv

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目

```bash
git clone https://github.com/your-username/alicloud-ops-mcp.git
cd alicloud-ops-mcp
```

### 3. 一键安装

```bash
# 运行安装脚本（推荐）
./install.sh

# 或者手动安装
uv sync
cp .env.example .env
# 编辑 .env 文件，填入你的阿里云凭证
```

### 4. 配置环境变量

编辑 `.env` 文件：

```env
ALIBABA_CLOUD_ACCESS_KEY_ID="your_access_key_id"
ALIBABA_CLOUD_ACCESS_KEY_SECRET="your_access_key_secret"
ALIBABA_CLOUD_REGION="cn-beijing"
```

### 5. 验证安装

```bash
# 运行验证脚本
uv run python verify_setup.py

# 测试服务器启动
uv run python complete_fastmcp_server.py
```

如果看到 "Server is ready to accept connections." 说明安装成功。

## Amazon Q CLI 配置

在 `~/.aws/amazonq/mcp.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "alibaba-cloud-ops-mcp-server": {
      "timeout": 30000,
      "command": "uv",
      "args": [
        "--directory",
        "/绝对路径/to/alicloud-ops-mcp",
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
}
```

**重要提示：** 将 `/绝对路径/to/alicloud-ops-mcp` 替换为项目的实际绝对路径。

### 配置示例

假设项目位于 `/home/user/alicloud-ops-mcp`：

```json
{
  "mcpServers": {
    "alibaba-cloud-ops-mcp-server": {
      "timeout": 30000,
      "command": "uv",
      "args": [
        "--directory",
        "/home/user/alicloud-ops-mcp",
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
}
```

## 支持的服务

| 服务 | 功能 | 状态 |
|------|------|------|
| **ECS** | 云服务器管理、实例操作、镜像管理 | ✅ |
| **VPC** | 虚拟私有云、网络配置、安全组 | ✅ |
| **RDS** | 关系型数据库管理、备份恢复 | ✅ |
| **OSS** | 对象存储、文件上传下载 | ✅ |
| **CloudMonitor** | 云监控、告警管理、指标查询 | ✅ |
| **OOS** | 运维编排、自动化任务 | ✅ |

## 开发说明

### 项目结构

```
alicloud-ops-mcp/
├── pyproject.toml              # 项目配置和依赖
├── requirements.txt            # 依赖列表（兼容性）
├── complete_fastmcp_server.py  # 主服务器文件
├── alibaba_cloud_ops_mcp_server/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py              # 服务器核心逻辑
│   ├── config.py              # 配置管理
│   └── tools/                 # 各服务工具
│       ├── __init__.py
│       ├── api_tools.py       # 通用 API 工具
│       ├── cms_tools.py       # CloudMonitor 工具
│       ├── common_api_tools.py # 公共 API 工具
│       ├── oos_tools.py       # OOS 工具
│       └── oss_tools.py       # OSS 工具
├── .env.example               # 环境变量模板
├── .env                       # 环境变量（需要创建）
├── install.sh                 # 安装脚本
├── verify_setup.py            # 验证脚本
├── README.md                  # 中文文档
├── README_EN.md               # 英文文档
└── LICENSE
```

### 使用 uv 进行开发

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 运行服务器
uv run python complete_fastmcp_server.py

# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 更新依赖
uv sync --upgrade

# 查看依赖树
uv tree
```

### Python 版本管理

项目在 `pyproject.toml` 中指定了 Python 版本要求：

```toml
requires-python = ">=3.10"
```

uv 会自动：
- 检测并安装合适的 Python 版本
- 创建隔离的虚拟环境
- 管理所有依赖关系
- 确保跨平台兼容性

## 故障排除

### 常见问题

#### 1. Permission denied (os error 13)

**原因：** 配置错误或权限问题

**解决方案：**
```bash
# 确保使用 uv 命令而不是直接的 python 路径
uv run python complete_fastmcp_server.py

# 检查项目路径是否正确
pwd

# 确保脚本有执行权限
chmod +x complete_fastmcp_server.py
```

#### 2. Python 版本不兼容

**错误信息：** `Could not find a version that satisfies the requirement fastmcp>=2.8.0`

**解决方案：**
```bash
# uv 会自动处理 Python 版本，无需手动安装
uv sync

# 如果仍有问题，清理并重新安装
uv clean
uv sync
```

#### 3. 依赖安装失败

**解决方案：**
```bash
# 清理缓存并重新安装
uv clean
uv sync

# 查看详细错误信息
uv sync --verbose
```

#### 4. 环境变量未加载

**解决方案：**
```bash
# 确保 .env 文件存在且格式正确
ls -la .env
cat .env

# 检查环境变量格式
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Access Key ID:', os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID', 'Not found'))
print('Region:', os.getenv('ALIBABA_CLOUD_REGION', 'Not found'))
"
```

#### 5. MCP 服务器无法启动

**解决方案：**
```bash
# 检查 Amazon Q CLI 配置
cat ~/.aws/amazonq/mcp.json

# 验证路径是否正确
ls -la /绝对路径/to/alicloud-ops-mcp/complete_fastmcp_server.py

# 测试服务器直接启动
cd /绝对路径/to/alicloud-ops-mcp
uv run python complete_fastmcp_server.py
```

### 调试模式

启用详细日志：

```bash
# 设置环境变量启用调试
export FASTMCP_LOG_LEVEL=DEBUG
uv run python complete_fastmcp_server.py

# 或者在 .env 文件中设置
echo "FASTMCP_LOG_LEVEL=DEBUG" >> .env
```

### 验证配置

运行完整的环境检查：

```bash
# 运行验证脚本
uv run python verify_setup.py

# 检查特定组件
uv run python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import fastmcp
    print(f'FastMCP version: {fastmcp.__version__}')
except ImportError as e:
    print(f'FastMCP import error: {e}')

try:
    from alibaba_cloud_ops_mcp_server import server
    print('Server module loaded successfully')
except ImportError as e:
    print(f'Server module error: {e}')
"
```

## 性能优化

### 启动优化

```bash
# 预编译 Python 字节码
uv run python -m compileall .

# 使用更快的启动选项
uv run python -O complete_fastmcp_server.py
```

### 内存优化

在 `.env` 文件中添加：

```env
# 限制内存使用
PYTHONHASHSEED=0
PYTHONDONTWRITEBYTECODE=1
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 安装开发依赖 (`uv sync --dev`)
4. 运行测试 (`uv run pytest`)
5. 提交更改 (`git commit -m 'Add some amazing feature'`)
6. 推送到分支 (`git push origin feature/amazing-feature`)
7. 创建 Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/alicloud-ops-mcp.git
cd alicloud-ops-mcp

# 安装开发依赖
uv sync --dev

# 设置 pre-commit hooks
uv run pre-commit install

# 运行测试
uv run pytest

# 代码格式化
uv run black .
uv run isort .

# 类型检查
uv run mypy .
```

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果遇到问题，请：

1. 查看 [故障排除](#故障排除) 部分
2. 运行 `uv run python verify_setup.py` 检查环境
3. 查看 [GitHub Issues](https://github.com/your-username/alicloud-ops-mcp/issues)
4. 创建新的 Issue 报告问题

### 获取帮助

- 📖 [文档](https://github.com/your-username/alicloud-ops-mcp/wiki)
- 🐛 [报告 Bug](https://github.com/your-username/alicloud-ops-mcp/issues/new?template=bug_report.md)
- 💡 [功能请求](https://github.com/your-username/alicloud-ops-mcp/issues/new?template=feature_request.md)
- 💬 [讨论](https://github.com/your-username/alicloud-ops-mcp/discussions)

## 更新日志

### v0.9.2 (2024-12-XX)
- ✨ 支持使用 uv 进行包管理
- 🚀 简化安装和配置流程
- 🐛 改进错误处理和调试信息
- 📚 更新文档和故障排除指南
- 🔧 添加环境验证脚本
- 📦 添加一键安装脚本

### v0.9.1
- 🔧 修复依赖版本兼容性问题
- 📝 改进文档结构
- 🐛 修复环境变量加载问题

### v0.9.0
- 🎉 初始版本发布
- ✅ 支持 ECS、VPC、RDS、OSS、CloudMonitor、OOS 服务
- 🔐 支持阿里云访问凭证配置
- 📖 完整的文档和示例

## 致谢

感谢所有贡献者和社区成员的支持！

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
