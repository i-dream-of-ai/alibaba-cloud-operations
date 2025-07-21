# Alibaba Cloud Ops MCP Server

**This is an adaptation of the Alibaba Cloud Ops MCP Server specifically for Amazon Q Developer CLI integration.**

[![GitHub stars](https://img.shields.io/github/stars/RadiumGu/alicloud-ops-mcp?style=social)](https://github.com/RadiumGu/alicloud-ops-mcp)

[中文版本](./README_zh.md)

Alibaba Cloud Ops MCP Server is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that provides seamless integration with Alibaba Cloud APIs, enabling AI assistants to operate resources on Alibaba Cloud, supporting ECS, Cloud Monitor, OOS, and other widely used cloud products.

## Features

- **Comprehensive API Support**: Access to ECS, VPC, RDS, OSS, CloudMonitor and more
- **Simple Integration**: Easy to integrate with any MCP-compatible AI assistant
- **Secure Authentication**: Uses Alibaba Cloud AccessKey for secure API access
- **Flexible Deployment**: Can be deployed locally or in cloud environments
- **Extensive Documentation**: Well-documented tools and examples

## Quick Start

### Prerequisites

- Alibaba Cloud Account with AccessKey ID and Secret
- Python 3.8+ environment
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/RadiumGu/alicloud-ops-mcp.git
cd alicloud-ops-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in your project directory with the following content:

```
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
ALIBABA_CLOUD_REGION=cn-beijing
```

To use `alicloud-ops-mcp` with Amazon Q CLI or other MCP clients, add the following configuration to your MCP configuration file (e.g., `~/.aws/amazonq/mcp.json`):

```json
{
  "mcpServers": {
    "alibaba-cloud-ops-mcp-server": {
      "timeout": 30000,
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "/path/to/alicloud-ops-mcp/complete_fastmcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/path/to/alicloud-ops-mcp"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Replace `/path/to/your/venv` and `/path/to/alicloud-ops-mcp` with your actual paths.

### Running Locally

Run the server:
```bash
python complete_fastmcp_server.py
```

## Project Structure

```
alicloud-ops-mcp/
├── alibaba_cloud_ops_mcp_server/     # Main package
│   ├── __init__.py
│   ├── __main__.py
│   ├── alibabacloud/                 # Alibaba Cloud API utilities
│   │   ├── __init__.py
│   │   ├── api_meta_client.py
│   │   ├── exception.py
│   │   ├── static/
│   │   └── utils.py
│   ├── config.py                     # Configuration settings
│   ├── server.py                     # Server implementation
│   └── tools/                        # Tool implementations
│       ├── __init__.py
│       ├── api_tools.py              # General API tools
│       ├── cms_tools.py              # CloudMonitor tools
│       ├── common_api_tools.py       # Common API utilities
│       ├── oos_tools.py              # OOS tools
│       └── oss_tools.py              # OSS tools
├── complete_fastmcp_server.py        # Main server entry point
├── .env                              # Environment variables (create this)
├── requirements.txt                  # Dependencies
├── README.md                         # Documentation
└── README_zh.md                      # Chinese documentation
```

## Available Tools

| **Product** | **Tool** | **Function** | **Implementation** | **Status** |
| --- | --- | --- | --- | --- |
| ECS | RunCommand | Run Command | OOS | Done |
| | StartInstances | Start Instances | OOS | Done |
| | StopInstances | Stop Instances | OOS | Done |
| | RebootInstances | Reboot Instances | OOS | Done |
| | DescribeInstances | View Instances | API | Done |
| | DescribeRegions | View Regions | API | Done |
| | DescribeZones | View Zones | API | Done |
| | DescribeAvailableResource | View Resource Inventory | API | Done |
| | DescribeImages | View Images | API | Done |
| | DescribeSecurityGroups | View Security Groups | API | Done |
| | RunInstances | Create Instances | OOS | Done |
| | DeleteInstances | Delete Instances | API | Done |
| | ResetPassword | Modify Password | OOS | Done |
| | ReplaceSystemDisk | Replace Operating System | OOS | Done |
| VPC | DescribeVpcs | View VPCs | API | Done |
| | DescribeVSwitches | View VSwitches | API | Done |
| RDS | DescribeDBInstances | List RDS Instances | API | Done |
|  | StartDBInstances | Start the RDS instance | OOS | Done |
|  | StopDBInstances | Stop the RDS instance | OOS | Done |
|  | RestartDBInstances | Restart the RDS instance | OOS | Done |
| OSS | ListBuckets | List Bucket | API | Done |
|  | PutBucket | Create Bucket | API | Done |
|  | DeleteBucket | Delete Bucket | API | Done |
|  | ListObjects | View object information in the bucket | API | Done |
| CloudMonitor | GetCpuUsageData | Get CPU Usage Data for ECS Instances | API | Done |
| | GetCpuLoadavgData | Get CPU One-Minute Average Load Metric Data | API | Done |
| | GetCpuloadavg5mData | Get CPU Five-Minute Average Load Metric Data | API | Done |
| | GetCpuloadavg15mData | Get CPU Fifteen-Minute Average Load Metric Data | API | Done |
| | GetMemUsedData | Get Memory Usage Metric Data | API | Done |
| | GetMemUsageData | Get Memory Utilization Metric Data | API | Done |
| | GetDiskUsageData | Get Disk Utilization Metric Data | API | Done |
| | GetDiskTotalData | Get Total Disk Partition Capacity Metric Data | API | Done |
| | GetDiskUsedData | Get Disk Partition Usage Metric Data | API | Done |

## MCP Marketplace Integration

* [Cline](https://cline.bot/mcp-marketplace)
* [Cursor](https://docs.cursor.com/tools)
* [ModelScope](https://www.modelscope.cn/mcp/servers/@aliyun/alibaba-cloud-ops-mcp-server)
* [Lingma](https://lingma.aliyun.com/)
* [Smithery AI](https://smithery.ai/server/@aliyun/alibaba-cloud-ops-mcp-server)
* [FC-Function AI](https://cap.console.aliyun.com/template-detail?template=237)
* [Alibaba Cloud Model Studio](https://bailian.console.aliyun.com/?tab=mcp#/mcp-market/detail/alibaba-cloud-ops)

## Development

### Adding New Tools

1. Create a new function in the appropriate tool module
2. Decorate it with `@tools.append`
3. Add proper documentation and type hints
4. Register the tool in the main server file

Example:
```python
@tools.append
def my_new_tool(param1: str, param2: int = 10) -> str:
    """
    Description of what the tool does
    
    Args:
        param1: Description of param1
        param2: Description of param2, defaults to 10
        
    Returns:
        Description of the return value
    """
    # Implementation
    return result
```

### Testing

To test your tools locally:

```bash
python test_oss.py  # Example for testing OSS tools
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you have any questions, please join the [Alibaba Cloud Ops MCP discussion group](https://qr.dingtalk.com/action/joingroup?code=v1,k1,iFxYG4jjLVh1jfmNAkkclji7CN5DSIdT+jvFsLyI60I=&_dt_no_comment=1&origin=11) (DingTalk group: 113455011677) for discussion.

<img src="https://oos-public-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/alibaba-cloud-ops-mcp-server/Alibaba-Cloud-Ops-MCP-User-Group-en.png" width="500">
