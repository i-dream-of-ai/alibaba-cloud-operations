# Q CLI 兼容性临时解决方案

## 问题描述

Amazon Q CLI 的 MCP 客户端实现与标准 MCP 协议存在兼容性问题：
1. 发送的初始化通知格式为 `"method": "initialized"`，而标准格式应为 `"method": "notifications/initialized"`
2. 工具列表请求在初始化完成前发送，导致请求失败

## 解决方案

创建了一个兼容性适配器 `qcli_compatible_server.py`，它：
- 处理 Q CLI 的非标准初始化通知格式
- 正确管理初始化状态
- 提供完整的工具列表和调用功能
- 保持与原始阿里云 MCP 服务器相同的功能

## 文件说明

### 核心文件
- `qcli_compatible_server.py` - 兼容性适配器主文件
- `qcli_server` - 启动脚本（已设置可执行权限）

### 测试文件
- `test_compatible.sh` - 兼容性测试脚本
- `debug_server.py` - 调试版本服务器
- `minimal_test.py` - 最小化测试

## 使用方法

### 1. 确认配置已更新
MCP 配置文件 `~/.aws/amazonq/mcp.json` 已更新为使用兼容服务器：
```json
{
  "alibaba-cloud-ops-mcp-server": {
    "command": "/Users/glei/genai/alibaba-cloud-ops-mcp-server/qcli_server",
    "args": ["--services", "ecs,vpc,rds,oss"],
    "env": {
      "ALIBABA_CLOUD_ACCESS_KEY_ID": "your-access-key-id",
      "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "your-access-key-secret",
      "ALIBABA_CLOUD_REGION": "cn-beijing"
    }
  }
}
```

### 2. 重启 Q CLI
```bash
# 如果 Q CLI 正在运行，先退出
# 然后重新启动
q chat
```

### 3. 测试功能
在 Q CLI 中测试：
```
你能列出可用的阿里云工具吗？
```

## 可用工具

兼容服务器提供以下工具：

### 核心工具
- `PromptUnderstanding` - 理解用户查询并转换为阿里云专家建议
- `ListAPIs` - 获取服务的 API 列表
- `GetAPIInfo` - 获取特定 API 的详细信息
- `CommonAPICaller` - 执行 API 调用

### ECS 管理工具
- `OOS_RunCommand` - 批量在 ECS 实例上运行命令
- `OOS_StartInstances` - 批量启动 ECS 实例
- `OOS_StopInstances` - 批量停止 ECS 实例
- `OOS_RebootInstances` - 批量重启 ECS 实例
- `OOS_RunInstances` - 批量创建 ECS 实例
- `OOS_ResetPassword` - 批量修改 ECS 实例密码
- `OOS_ReplaceSystemDisk` - 批量替换系统盘

### RDS 管理工具
- `OOS_StartRDSInstances` - 批量启动 RDS 实例
- `OOS_StopRDSInstances` - 批量停止 RDS 实例
- `OOS_RebootRDSInstances` - 批量重启 RDS 实例

### 监控工具
- `CMS_GetCpuUsageData` - 获取 CPU 使用率
- `CMS_GetCpuLoadavgData` - 获取 CPU 负载
- `CMS_GetMemUsedData` - 获取内存使用量
- `CMS_GetMemUsageData` - 获取内存利用率
- `CMS_GetDiskUsageData` - 获取磁盘利用率

### OSS 工具
- `OSS_ListBuckets` - 列出存储空间
- `OSS_ListObjects` - 列出对象
- `OSS_PutBucket` - 创建存储空间
- `OSS_DeleteBucket` - 删除存储空间

### Claude AI 工具
- `list_claude_models` - 列出可用的 Claude 模型
- `generate_claude_completion` - 生成 Claude 完成

## 故障排除

### 1. 权限问题
确保启动脚本有执行权限：
```bash
chmod +x /Users/glei/genai/alibaba-cloud-ops-mcp-server/qcli_server
```

### 2. 环境变量问题
检查阿里云凭证是否正确设置在 MCP 配置中。

### 3. 依赖问题
确保虚拟环境中安装了所有依赖：
```bash
cd /Users/glei/genai/alibaba-cloud-ops-mcp-server
source .venv/bin/activate
pip install -e .
```

### 4. 测试兼容性
运行测试脚本验证功能：
```bash
./test_compatible.sh
```

## 日志和调试

兼容服务器会输出详细的日志信息，包括：
- 服务器启动信息
- 初始化状态
- 工具调用详情
- 错误信息

## 注意事项

1. **临时解决方案**：这是一个临时解决方案，等待 Amazon Q CLI 团队修复 MCP 协议兼容性问题。

2. **功能完整性**：兼容服务器提供与原始服务器相同的功能，只是增加了协议兼容性处理。

3. **性能影响**：由于增加了适配层，可能会有轻微的性能影响，但在正常使用中应该不明显。

4. **更新建议**：定期检查 Amazon Q CLI 更新，一旦官方修复了兼容性问题，可以切换回原始服务器。

## 联系支持

如果遇到问题，可以：
1. 检查日志输出
2. 运行测试脚本验证
3. 向 Amazon Q 团队报告 MCP 协议兼容性问题
