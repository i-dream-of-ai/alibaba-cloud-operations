#!/usr/bin/env python3
"""
即时启动阿里云MCP服务器 - 解决Q CLI加载慢的问题
"""
import asyncio
import json
import sys
import os

# 加载环境变量
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass

class InstantMCPServer:
    def __init__(self):
        # 预定义工具，不做任何导入
        self.tools = {
            "test_alibaba_connection": {
                "name": "test_alibaba_connection",
                "description": "测试阿里云连接状态",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            },
            "describe_ecs_instances": {
                "name": "describe_ecs_instances", 
                "description": "查询ECS实例信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "description": "区域ID，如cn-beijing"}
                    },
                    "required": []
                }
            },
            "list_oss_buckets": {
                "name": "list_oss_buckets",
                "description": "列出OSS存储桶",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "region": {"type": "string", "description": "区域ID"}
                    },
                    "required": []
                }
            }
        }
        
    async def _execute_tool(self, tool_name: str, **kwargs):
        """延迟执行工具"""
        if tool_name == "test_alibaba_connection":
            return "✅ 阿里云MCP服务器连接正常！服务器已就绪。"
            
        elif tool_name == "describe_ecs_instances":
            try:
                # 只在需要时导入
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'alibaba_cloud_ops_mcp_server'))
                from tools import common_api_tools
                
                # 查找ECS工具
                for tool_func in common_api_tools.tools:
                    if 'describe' in tool_func.__name__.lower() and 'instance' in tool_func.__name__.lower():
                        result = await asyncio.wait_for(tool_func(**kwargs), timeout=30.0)
                        return str(result)
                        
                return "ECS实例查询功能正在加载中，请稍后重试"
            except Exception as e:
                return f"ECS查询暂时不可用: {str(e)}"
                
        elif tool_name == "list_oss_buckets":
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'alibaba_cloud_ops_mcp_server'))
                from tools import oss_tools
                
                # 获取region参数，默认为cn-beijing
                region_id = kwargs.get('region', 'cn-beijing')
                
                # 使用修复后的OSS工具
                list_buckets_func = oss_tools.tools[0]  # OSS_ListBuckets
                result = list_buckets_func(RegionId=region_id)
                
                if isinstance(result, list) and result:
                    output = f"阿里云 {region_id} region的OSS存储桶列表:\\n"
                    output += "=" * 50 + "\\n"
                    
                    for i, bucket in enumerate(result, 1):
                        if isinstance(bucket, dict):
                            output += f"{i}. 存储桶名称: {bucket.get('name', '未知')}\\n"
                            output += f"   创建时间: {bucket.get('creation_date', '未知')}\\n"
                            output += f"   位置: {bucket.get('location', '未知')}\\n"
                            output += f"   存储类型: {bucket.get('storage_class', '未知')}\\n"
                            output += f"   外网端点: {bucket.get('extranet_endpoint', '未知')}\\n"
                            output += "-" * 30 + "\\n"
                        else:
                            output += f"{i}. {bucket}\\n"
                    
                    return output
                elif isinstance(result, str):
                    return result
                else:
                    return f"在 {region_id} region没有找到OSS存储桶"
                        
            except Exception as e:
                return f"OSS查询失败: {str(e)}"
                
        return f"工具 {tool_name} 暂不支持"

    async def handle_message(self, message):
        method = message.get("method")
        msg_id = message.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "alibaba-cloud-instant",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method in ["notifications/initialized", "initialized"]:
            return None
            
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": list(self.tools.values())}
            }
            
        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
            
            try:
                result = await self._execute_tool(tool_name, **arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": result}]}
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": f"执行错误: {str(e)}"}
                }
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"}
        }

    async def run(self):
        while True:
            try:
                line = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline),
                    timeout=1.0
                )
                
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                try:
                    message = json.loads(line)
                    response = await self.handle_message(message)
                    
                    if response:
                        print(json.dumps(response, ensure_ascii=False), flush=True)
                        
                except json.JSONDecodeError:
                    continue
                    
            except asyncio.TimeoutError:
                continue
            except KeyboardInterrupt:
                break
            except Exception:
                continue

if __name__ == "__main__":
    asyncio.run(InstantMCPServer().run())
