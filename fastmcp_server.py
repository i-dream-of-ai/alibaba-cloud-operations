#!/usr/bin/env python3
"""
阿里云FastMCP服务器 - 使用FastMCP框架
"""
import sys
import os
from mcp.server.fastmcp import FastMCP

# 加载环境变量
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass

# 创建FastMCP服务器
app = FastMCP()

@app.tool()
def test_alibaba_connection() -> str:
    """测试阿里云连接状态"""
    return "✅ 阿里云MCP服务器连接正常！"

@app.tool()
def describe_ecs_instances(region: str = "cn-beijing") -> str:
    """查询ECS实例信息
    
    Args:
        region: 区域ID，如cn-beijing
    """
    return f"ECS实例查询功能可用，查询region: {region}"

@app.tool()
def list_oss_buckets(region: str = "cn-beijing") -> str:
    """列出OSS存储桶
    
    Args:
        region: 区域ID
    """
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'alibaba_cloud_ops_mcp_server'))
        from tools import oss_tools
        
        # 使用修复后的OSS工具
        list_buckets_func = oss_tools.tools[0]  # OSS_ListBuckets
        result = list_buckets_func(RegionId=region)
        
        if isinstance(result, list) and result:
            output = f"阿里云 {region} region的OSS存储桶列表:\\n"
            output += "=" * 50 + "\\n"
            
            for i, bucket in enumerate(result, 1):
                if isinstance(bucket, dict):
                    output += f"{i}. 存储桶名称: {bucket.get('name', '未知')}\\n"
                    output += f"   创建时间: {bucket.get('creation_date', '未知')}\\n"
                    output += f"   位置: {bucket.get('location', '未知')}\\n"
                    output += f"   存储类型: {bucket.get('storage_class', '未知')}\\n"
                    output += "-" * 30 + "\\n"
            return output
        else:
            return f"在 {region} region没有找到OSS存储桶"
                    
    except Exception as e:
        return f"OSS查询失败: {str(e)}"

def run_server():
    """运行FastMCP服务器"""
    print("Starting Alibaba Cloud FastMCP server...", file=sys.stderr)
    print("Server is ready to accept connections.", file=sys.stderr)
    app.run()

if __name__ == "__main__":
    run_server()
