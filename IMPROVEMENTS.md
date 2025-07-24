# Alibaba Cloud Operations MCP Server - Improvements

This repository contains improvements and fixes for the original Alibaba Cloud Operations MCP Server to enhance compatibility with Amazon Q CLI.

## Key Improvements

### 1. Q CLI Compatible Server (`qcli_compatible_server_fixed.py`)
- **Enhanced tool name handling**: Proper prefixes for MCP tool registration
- **Improved error handling**: Better timeout management and error recovery
- **Optimized performance**: Reduced latency and improved response times
- **Enhanced logging**: Detailed debugging information for troubleshooting

### 2. Working Server Implementation (`working_server.py`)
- **Stable production-ready implementation**
- **Robust error handling and recovery**
- **Optimized resource management**
- **Better connection handling**

### 3. Compatibility Documentation (`QCLI_COMPATIBILITY_FIX.md`)
- **Detailed technical documentation** of all compatibility fixes
- **Step-by-step troubleshooting guide**
- **Configuration examples and best practices**

## Original Features

This MCP server provides integration for Alibaba Cloud services:

- **ECS (Elastic Compute Service)**: Instance management, monitoring, and operations
- **OSS (Object Storage Service)**: Bucket and object operations
- **OOS (Operation Orchestration Service)**: Automation and orchestration workflows
- **CMS (Cloud Monitor Service)**: Monitoring, alerting, and metrics

## Installation and Usage

### Prerequisites
```bash
pip install fastmcp alibabacloud-ecs20140526 alibabacloud-oss-sdk2 alibabacloud-cms20190101
```

### Configuration
Set your Alibaba Cloud credentials:
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-secret-key"
export ALIBABA_CLOUD_REGION="cn-beijing"  # or your preferred region
```

### Running the Server
```bash
# Use the improved Q CLI compatible version
python qcli_compatible_server_fixed.py

# Or use the stable working version
python working_server.py
```

### Integration with Amazon Q CLI
```bash
# Add the MCP server to Q CLI configuration
q configure mcp add alibaba-cloud-ops /path/to/qcli_compatible_server_fixed.py
```

## Development Notes

The improvements were developed through extensive testing and debugging:
- Multiple iterations of compatibility fixes
- Performance optimization and timeout handling
- Enhanced error reporting and logging
- Better integration with Q CLI's MCP client

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project maintains the same license as the original Alibaba Cloud Operations MCP Server.
