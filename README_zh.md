# Alibaba Cloud Ops MCP Server

[![GitHub stars](https://img.shields.io/github/stars/RadiumGu/alicloud-ops-mcp?style=social)](https://github.com/RadiumGu/alicloud-ops-mcp)

[English README](./README_updated.md)

Alibaba Cloud Ops MCP Server是一个[模型上下文协议（MCP）](https://modelcontextprotocol.io/introduction)服务器，提供与阿里云API的无缝集成，使AI助手能够操作阿里云上的资源，支持ECS、云监控、OOS等广泛使用的云产品。

## 特点

- **全面的API支持**：访问ECS、VPC、RDS、OSS、云监控等服务
- **简单集成**：易于与任何兼容MCP的AI助手集成
- **安全认证**：使用阿里云AccessKey进行安全API访问
- **灵活部署**：可以在本地或云环境中部署
- **详尽文档**：提供完善的工具文档和示例

## 快速开始

### 前提条件

- 阿里云账户及AccessKey ID和Secret
- Python 3.8+环境
- 虚拟环境（推荐）

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/RadiumGu/alicloud-ops-mcp.git
cd alicloud-ops-mcp
```

2. 创建并激活虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Windows上: .venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

### 配置

在项目目录中创建一个`.env`文件，内容如下：

```
ALIBABA_CLOUD_ACCESS_KEY_ID=你的访问密钥ID
ALIBABA_CLOUD_ACCESS_KEY_SECRET=你的访问密钥SECRET
ALIBABA_CLOUD_REGION=cn-beijing
```

要将`alicloud-ops-mcp`与Amazon Q CLI或其他MCP客户端一起使用，请将以下配置添加到您的MCP配置文件中（例如`~/.aws/amazonq/mcp.json`）：

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

请将`/path/to/your/venv`和`/path/to/alicloud-ops-mcp`替换为您的实际路径。

### 本地运行

运行服务器：
```bash
python complete_fastmcp_server.py
```

## 项目结构

```
alicloud-ops-mcp/
├── alibaba_cloud_ops_mcp_server/     # 主包
│   ├── __init__.py
│   ├── __main__.py
│   ├── alibabacloud/                 # 阿里云API工具
│   │   ├── __init__.py
│   │   ├── api_meta_client.py
│   │   ├── exception.py
│   │   ├── static/
│   │   └── utils.py
│   ├── config.py                     # 配置设置
│   ├── server.py                     # 服务器实现
│   └── tools/                        # 工具实现
│       ├── __init__.py
│       ├── api_tools.py              # 通用API工具
│       ├── cms_tools.py              # 云监控工具
│       ├── common_api_tools.py       # 通用API实用程序
│       ├── oos_tools.py              # OOS工具
│       └── oss_tools.py              # OSS工具
├── complete_fastmcp_server.py        # 主服务器入口点
├── .env                              # 环境变量（需要创建）
├── requirements.txt                  # 依赖项
├── README.md                         # 文档
└── README_zh.md                      # 中文文档
```

## 可用工具

| **产品** | **工具** | **功能** | **实现方式** | **状态** |
| --- | --- | --- | --- | --- |
| ECS | RunCommand | 运行命令 | OOS | 完成 |
|  | StartInstances | 启动实例 | OOS | 完成 |
|  | StopInstances | 停止实例 | OOS | 完成 |
|  | RebootInstances | 重启实例 | OOS | 完成 |
|  | DescribeInstances | 查看实例 | API | 完成 |
|  | DescribeRegions | 查看地域 | API | 完成 |
|  | DescribeZones | 查看可用区 | API | 完成 |
|  | DescribeAvailableResource | 查看资源库存 | API | 完成 |
|  | DescribeImages | 查看镜像 | API | 完成 |
|  | DescribeSecurityGroups | 查看安全组 | API | 完成 |
|  | RunInstances | 创建实例 | OOS | 完成 |
|  | DeleteInstances | 删除实例 | API | 完成 |
|  | ResetPassword | 修改密码 | OOS | 完成 |
|  | ReplaceSystemDisk | 更换操作系统 | OOS | 完成 |
| VPC | DescribeVpcs | 查看VPC | API | 完成 |
|  | DescribeVSwitches | 查看VSwitch | API | 完成 |
| RDS | DescribeDBInstances | 查询数据库实例列表 | API | 完成 |
|  | StartDBInstances | 启动RDS实例 | OOS | 完成 |
|  | StopDBInstances | 暂停RDS实例 | OOS | 完成 |
|  | RestartDBInstances | 重启RDS实例 | OOS | 完成 |
| OSS | ListBuckets | 查看存储空间 | API | 完成 |
|  | PutBucket | 创建存储空间 | API | 完成 |
|  | DeleteBucket | 删除存储空间 | API | 完成 |
|  | ListObjects | 查看存储空间中的文件信息 | API | 完成 |
| CloudMonitor | GetCpuUsageData | 获取ECS实例的CPU使用率数据 | API | 完成 |
|  | GetCpuLoadavgData | 获取CPU一分钟平均负载指标数据 | API | 完成 |
|  | GetCpuloadavg5mData | 获取CPU五分钟平均负载指标数据 | API | 完成 |
|  | GetCpuloadavg15mData | 获取CPU十五分钟平均负载指标数据 | API | 完成 |
|  | GetMemUsedData | 获取内存使用量指标数据 | API | 完成 |
|  | GetMemUsageData | 获取内存利用率指标数据 | API | 完成 |
|  | GetDiskUsageData | 获取磁盘利用率指标数据 | API | 完成 |
|  | GetDiskTotalData | 获取磁盘分区总容量指标数据 | API | 完成 |
|  | GetDiskUsedData | 获取磁盘分区使用量指标数据 | API | 完成 |

## MCP市场集成

* [Cline](https://cline.bot/mcp-marketplace)
* [Cursor](https://docs.cursor.com/tools)
* [魔搭](https://www.modelscope.cn/mcp/servers/@aliyun/alibaba-cloud-ops-mcp-server)
* [通义灵码](https://lingma.aliyun.com/)
* [Smithery AI](https://smithery.ai/server/@aliyun/alibaba-cloud-ops-mcp-server)
* [FC-Function AI](https://cap.console.aliyun.com/template-detail?template=237)
* [阿里云百炼平台](https://bailian.console.aliyun.com/?tab=mcp#/mcp-market/detail/alibaba-cloud-ops)

## 开发

### 添加新工具

1. 在适当的工具模块中创建一个新函数
2. 使用`@tools.append`装饰器
3. 添加适当的文档和类型提示
4. 在主服务器文件中注册该工具

示例：
```python
@tools.append
def my_new_tool(param1: str, param2: int = 10) -> str:
    """
    描述工具的功能
    
    参数：
        param1: param1的描述
        param2: param2的描述，默认为10
        
    返回：
        返回值的描述
    """
    # 实现
    return result
```

### 测试

要在本地测试您的工具：

```bash
python test_oss.py  # 测试OSS工具的示例
```

## 贡献

欢迎贡献！请随时提交Pull Request。

1. Fork仓库
2. 创建您的特性分支（`git checkout -b feature/amazing-feature`）
3. 提交您的更改（`git commit -m 'Add some amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 打开Pull Request

## 许可证

该项目采用MIT许可证 - 详情请参阅LICENSE文件。

## 联系我们

如果您有任何疑问，欢迎加入 [Alibaba Cloud Ops MCP 交流群](https://qr.dingtalk.com/action/joingroup?code=v1,k1,iFxYG4jjLVh1jfmNAkkclji7CN5DSIdT+jvFsLyI60I=&_dt_no_comment=1&origin=11) (钉钉群：113455011677) 进行交流。

<img src="https://oos-public-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/alibaba-cloud-ops-mcp-server/Alibaba-Cloud-Ops-MCP-User-Group-zh.png" width="500">
