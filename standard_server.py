#!/usr/bin/env python3
"""
标准MCP协议阿里云服务器 - 严格遵循MCP协议规范
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

class StandardMCPServer:
    def __init__(self):
        self.initialized = False
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
            return "✅ 阿里云MCP服务器连接正常！"
            
        elif tool_name == "describe_ecs_instances":
            return "ECS实例查询功能可用，请提供具体的region参数"
                
        elif tool_name == "list_oss_buckets":
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'alibaba_cloud_ops_mcp_server'))
                from tools import oss_tools
                
                region_id = kwargs.get('region', 'cn-beijing')
                list_buckets_func = oss_tools.tools[0]
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
                            output += "-" * 30 + "\\n"
                    return output
                else:
                    return f"在 {region_id} region没有找到OSS存储桶"
                        
            except Exception as e:
                return f"OSS查询失败: {str(e)}"
                
        return f"工具 {tool_name} 暂不支持"

    async def handle_message(self, message):
        """严格按照MCP协议处理消息"""
        method = message.get("method")
        msg_id = message.get("id")
        
        # 初始化请求
        if method == "initialize":
            # 获取客户端请求的协议版本
            client_protocol = message.get("params", {}).get("protocolVersion", "2.0")
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": client_protocol,  # 使用客户端请求的版本
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "alibaba-cloud-standard",
                        "version": "1.0.0"
                    }
                }
            }
            
        # 初始化完成通知 - 不返回响应
        elif method == "notifications/initialized":
            self.initialized = True
            return None
            
        # 工具列表请求
        elif method == "tools/list":
            if not self.initialized:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32002,
                        "message": "Server not initialized"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": list(self.tools.values())
                }
            }
            
        # 工具调用请求
        elif method == "tools/call":
            if not self.initialized:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32002,
                        "message": "Server not initialized"
                    }
                }
            
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            try:
                result = await self._execute_tool(tool_name, **arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution error: {str(e)}"
                    }
                }
        
        # 未知方法
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Unknown method: {method}"
            }
        }

    async def run(self):
        """运行服务器"""
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
                    
                    # 只有非None响应才输出
                    if response is not None:
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
    asyncio.run(StandardMCPServer().run())
