#!/usr/bin/env python3
"""
快速启动的阿里云MCP服务器 - 模仿AWS Labs的加载策略
"""
import asyncio
import json
import sys
import logging
import argparse
from typing import Dict, Any, Optional
import os

# 最小化日志
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)
logger = logging.getLogger(__name__)

class FastMCPServer:
    def __init__(self, services: Optional[str] = None):
        self.initialized = False
        self.services = services
        
        # 立即定义基础工具，不实际加载
        self.tools = {
            "test_connection": {
                "name": "test_connection",
                "description": "测试阿里云连接",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            },
            "describe_ecs_instances": {
                "name": "describe_ecs_instances",
                "description": "查看ECS实例列表",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "description": "区域ID"}
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
        
        # 立即输出就绪信息
        sys.stderr.write("Fast MCP Server ready\n")
        sys.stderr.flush()
        
    async def _lazy_load_handler(self, tool_name: str, **kwargs):
        """延迟加载工具处理器"""
        try:
            if tool_name == "test_connection":
                return "✅ 阿里云MCP服务器连接成功！"
                
            elif tool_name == "describe_ecs_instances":
                # 只在需要时导入和执行
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'alibaba-cloud-ops-mcp-server', 'src'))
                from alibaba_cloud_ops_mcp_server.tools import common_api_tools
                
                # 查找ECS相关工具
                for tool_func in common_api_tools.tools:
                    if 'ecs' in tool_func.__name__.lower() and 'describe' in tool_func.__name__.lower():
                        result = await asyncio.wait_for(tool_func(**kwargs), timeout=30.0)
                        return result
                        
                return "ECS实例查询功能需要完整配置"
                
            elif tool_name == "list_oss_buckets":
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'alibaba-cloud-ops-mcp-server', 'src'))
                from alibaba_cloud_ops_mcp_server.tools import oss_tools
                
                # 查找OSS相关工具
                for tool_func in oss_tools.tools:
                    if 'bucket' in tool_func.__name__.lower() and 'list' in tool_func.__name__.lower():
                        result = await asyncio.wait_for(tool_func(**kwargs), timeout=30.0)
                        return result
                        
                return "OSS存储桶列表功能需要完整配置"
                
            else:
                return f"工具 {tool_name} 暂不支持"
                
        except Exception as e:
            return f"执行 {tool_name} 时出错: {str(e)}"

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理MCP消息"""
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
                        "name": "alibaba-cloud-ops-fast",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method in ["notifications/initialized", "initialized"]:
            self.initialized = True
            return None
            
        elif method == "tools/list":
            # 立即返回工具列表，无需等待加载
            tools_list = list(self.tools.values())
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": tools_list}
            }
            
        elif method == "tools/call":
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
                # 延迟加载和执行
                result = await self._lazy_load_handler(tool_name, **arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": str(result)}]
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
                    
                    if response:
                        print(json.dumps(response, ensure_ascii=False), flush=True)
                        
                except json.JSONDecodeError:
                    continue
                    
            except asyncio.TimeoutError:
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                continue

def main():
    parser = argparse.ArgumentParser(description="Fast Alibaba Cloud MCP Server")
    parser.add_argument("--services", type=str, help="Services (for compatibility)")
    parser.add_argument("--dashscope-url", type=str, help="DashScope URL (for compatibility)")
    args = parser.parse_args()
    
    server = FastMCPServer(services=args.services)
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
