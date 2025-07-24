# Alibaba Cloud Operations MCP Server

An MCP server for Amazon Q CLI that provides operations for Alibaba Cloud services including ECS, VPC, RDS, OSS, CloudMonitor, OOS, and more.

English | [中文](README.md)

## Requirements

- Python 3.10+ (automatically managed by uv)
- [uv](https://docs.astral.sh/uv/) - Python package and project manager
- Alibaba Cloud access credentials

## Quick Start

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Project

```bash
git clone https://github.com/your-username/alicloud-ops-mcp.git
cd alicloud-ops-mcp
```

### 3. One-Click Installation

```bash
# Run installation script (recommended)
./install.sh

# Or manual installation
uv sync
cp .env.example .env
# Edit .env file with your Alibaba Cloud credentials
```

### 4. Configure Environment Variables

Edit the `.env` file:

```env
ALIBABA_CLOUD_ACCESS_KEY_ID="your_access_key_id"
ALIBABA_CLOUD_ACCESS_KEY_SECRET="your_access_key_secret"
ALIBABA_CLOUD_REGION="cn-beijing"
```

### 5. Verify Installation

```bash
# Run verification script
uv run python verify_setup.py

# Test server startup
uv run python complete_fastmcp_server.py
```

If you see "Server is ready to accept connections.", the installation is successful.

## Amazon Q CLI Configuration

Add the following configuration to `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "alibaba-cloud-ops-mcp-server": {
      "timeout": 30000,
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/alicloud-ops-mcp",
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

**Important:** Replace `/absolute/path/to/alicloud-ops-mcp` with the actual absolute path to your project.

### Configuration Example

Assuming the project is located at `/home/user/alicloud-ops-mcp`:

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

## Supported Services

| Service | Features | Status |
|---------|----------|--------|
| **ECS** | Instance management, operations, image management | ✅ |
| **VPC** | Virtual private cloud, network configuration, security groups | ✅ |
| **RDS** | Database management, backup and recovery | ✅ |
| **OSS** | Object storage, file upload/download | ✅ |
| **CloudMonitor** | Cloud monitoring, alarm management, metrics query | ✅ |
| **OOS** | Operation orchestration, automation tasks | ✅ |

## Development

### Project Structure

```
alicloud-ops-mcp/
├── pyproject.toml              # Project configuration and dependencies
├── requirements.txt            # Dependencies list (compatibility)
├── complete_fastmcp_server.py  # Main server file
├── alibaba_cloud_ops_mcp_server/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py              # Server core logic
│   ├── config.py              # Configuration management
│   └── tools/                 # Service tools
│       ├── __init__.py
│       ├── api_tools.py       # Generic API tools
│       ├── cms_tools.py       # CloudMonitor tools
│       ├── common_api_tools.py # Common API tools
│       ├── oos_tools.py       # OOS tools
│       └── oss_tools.py       # OSS tools
├── .env.example               # Environment variables template
├── .env                       # Environment variables (needs to be created)
├── install.sh                 # Installation script
├── verify_setup.py            # Verification script
├── README.md                  # Chinese documentation
├── README_EN.md               # English documentation
└── LICENSE
```

### Development with uv

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run server
uv run python complete_fastmcp_server.py

# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade

# View dependency tree
uv tree
```

### Python Version Management

The project specifies Python version requirements in `pyproject.toml`:

```toml
requires-python = ">=3.10"
```

uv automatically:
- Detects and installs the appropriate Python version
- Creates isolated virtual environments
- Manages all dependencies
- Ensures cross-platform compatibility

## Troubleshooting

### Common Issues

#### 1. Permission denied (os error 13)

**Cause:** Configuration error or permission issues

**Solution:**
```bash
# Ensure using uv command instead of direct python path
uv run python complete_fastmcp_server.py

# Check if project path is correct
pwd

# Ensure script has execute permissions
chmod +x complete_fastmcp_server.py
```

#### 2. Python Version Incompatibility

**Error message:** `Could not find a version that satisfies the requirement fastmcp>=2.8.0`

**Solution:**
```bash
# uv automatically handles Python versions, no manual installation needed
uv sync

# If issues persist, clean and reinstall
uv clean
uv sync
```

#### 3. Dependency Installation Failure

**Solution:**
```bash
# Clean cache and reinstall
uv clean
uv sync

# View detailed error information
uv sync --verbose
```

#### 4. Environment Variables Not Loaded

**Solution:**
```bash
# Ensure .env file exists and format is correct
ls -la .env
cat .env

# Check environment variable format
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Access Key ID:', os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID', 'Not found'))
print('Region:', os.getenv('ALIBABA_CLOUD_REGION', 'Not found'))
"
```

#### 5. MCP Server Cannot Start

**Solution:**
```bash
# Check Amazon Q CLI configuration
cat ~/.aws/amazonq/mcp.json

# Verify path is correct
ls -la /absolute/path/to/alicloud-ops-mcp/complete_fastmcp_server.py

# Test server direct startup
cd /absolute/path/to/alicloud-ops-mcp
uv run python complete_fastmcp_server.py
```

### Debug Mode

Enable verbose logging:

```bash
# Set environment variable to enable debugging
export FASTMCP_LOG_LEVEL=DEBUG
uv run python complete_fastmcp_server.py

# Or set in .env file
echo "FASTMCP_LOG_LEVEL=DEBUG" >> .env
```

### Configuration Verification

Run complete environment check:

```bash
# Run verification script
uv run python verify_setup.py

# Check specific components
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

## Performance Optimization

### Startup Optimization

```bash
# Precompile Python bytecode
uv run python -m compileall .

# Use faster startup options
uv run python -O complete_fastmcp_server.py
```

### Memory Optimization

Add to `.env` file:

```env
# Limit memory usage
PYTHONHASHSEED=0
PYTHONDONTWRITEBYTECODE=1
```

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`uv sync --dev`)
4. Run tests (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Create a Pull Request

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/your-username/alicloud-ops-mcp.git
cd alicloud-ops-mcp

# Install development dependencies
uv sync --dev

# Set up pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Code formatting
uv run black .
uv run isort .

# Type checking
uv run mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues, please:

1. Check the [Troubleshooting](#troubleshooting) section
2. Run `uv run python verify_setup.py` to check your environment
3. Check [GitHub Issues](https://github.com/your-username/alicloud-ops-mcp/issues)
4. Create a new Issue to report problems

### Getting Help

- 📖 [Documentation](https://github.com/your-username/alicloud-ops-mcp/wiki)
- 🐛 [Report Bug](https://github.com/your-username/alicloud-ops-mcp/issues/new?template=bug_report.md)
- 💡 [Feature Request](https://github.com/your-username/alicloud-ops-mcp/issues/new?template=feature_request.md)
- 💬 [Discussions](https://github.com/your-username/alicloud-ops-mcp/discussions)

## Changelog

### v0.9.2 (2024-12-XX)
- ✨ Support for uv package management
- 🚀 Simplified installation and configuration process
- 🐛 Improved error handling and debugging information
- 📚 Updated documentation and troubleshooting guide
- 🔧 Added environment verification script
- 📦 Added one-click installation script

### v0.9.1
- 🔧 Fixed dependency version compatibility issues
- 📝 Improved documentation structure
- 🐛 Fixed environment variable loading issues

### v0.9.0
- 🎉 Initial release
- ✅ Support for ECS, VPC, RDS, OSS, CloudMonitor, OOS services
- 🔐 Support for Alibaba Cloud access credential configuration
- 📖 Complete documentation and examples

## Acknowledgments

Thanks to all contributors and community members for their support!

---

**⭐ If this project helps you, please give it a Star!**
