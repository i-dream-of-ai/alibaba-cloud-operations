#!/usr/bin/env python3
"""
简化版阿里云MCP服务器 - 解决响应超时问题
"""
import asyncio
import json
import sys
import logging
import argparse
from typing import Dict, Any, Optional
import os

# 配置日志
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    def __init__(self, services: Optional[str] = None):
        self.initialized = False
        self.tools = self._create_basic_tools()
        
        # 立即输出启动信息
        sys.stderr.write("Simple MCP Server starting...\n")
        sys.stderr.flush()
        
    def _create_basic_tools(self):
        """创建基础工具，避免复杂的导入"""
        return {
            "test_connection": {
                "name": "test_connection",
                "description": "测试阿里云MCP连接",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "list_ecs_instances": {
                "name": "list_ecs_instances", 
                "description": "列出ECS实例",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "description": "区域"}
                    },
                    "required": []
                }
            }
        }
    
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
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "alibaba-cloud-ops-simple",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "notifications/initialized":
            self.initialized = True
            return None
            
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0", 
                "id": msg_id,
                "result": {
                    "tools": list(self.tools.values())
                }
            }
            
        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            
            if tool_name == "test_connection":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": "✅ 阿里云MCP服务器连接成功！"}]
                    }
                }
            elif tool_name == "list_ecs_instances":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": "ECS实例列表功能需要完整的阿里云SDK配置"}]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
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
        sys.stderr.write("Simple MCP Server ready\n")
        sys.stderr.flush()
        
        while True:
            try:
                # 非阻塞读取stdin
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
                logger.error(f"Error: {e}")
                continue

def main():
    parser = argparse.ArgumentParser(description="Simple Alibaba Cloud MCP Server")
    parser.add_argument("--services", type=str, help="Services (ignored in simple version)")
    args = parser.parse_args()
    
    server = SimpleMCPServer(services=args.services)
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
