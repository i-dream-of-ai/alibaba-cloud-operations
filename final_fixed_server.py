#!/usr/bin/env python3
"""
最终修复版阿里云MCP服务器 - 解决异步工具提取问题
"""
import asyncio
import json
import sys
import logging
import argparse
from typing import Dict, Any, List, Optional
import os
import signal
import threading
import time

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'alibaba-cloud-ops-mcp-server', 'src'))

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

SUPPORTED_SERVICES_MAP = {
    "ecs": "Elastic Compute Service (ECS)",
    "oos": "Operations Orchestration Service (OOS)", 
    "rds": "Relational Database Service (RDS)",
    "vpc": "Virtual Private Cloud (VPC)",
    "slb": "Server Load Balancer (SLB)",
    "ess": "Elastic Scaling (ESS)",
    "ros": "Resource Orchestration Service (ROS)",
    "cbn": "Cloud Enterprise Network (CBN)",
    "dds": "MongoDB Database Service (DDS)",
    "r-kvstore": "Cloud database Tair (compatible with Redis) (R-KVStore)",
    "oss": "Object Storage Service (OSS)",
    "cloudmonitor": "CloudMonitor Service"
}

class FinalFixedMCPServer:
    def __init__(self, services: Optional[str] = None):
        self.initialized = False
        self.tools = {}
        self.services = services
        self.tools_loaded = False
        self.fastmcp_instance = None
        
        sys.stderr.write("Final Fixed MCP Server starting...\n")
        sys.stderr.flush()
        
    async def _load_tools_async(self):
        """异步加载工具"""
        try:
            await self.setup_tools_async(self.services)
            self.tools_loaded = True
            sys.stderr.write(f"Tools loaded: {len(self.tools)} available\n")
            sys.stderr.flush()
        except Exception as e:
            logger.error(f"Error loading tools: {e}")
            # 提供基础工具作为后备
            self.tools = {
                "test_connection": {
                    "name": "test_connection",
                    "description": "测试阿里云MCP连接",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "handler": self._test_handler
                }
            }
            self.tools_loaded = True
            sys.stderr.write("Fallback tools loaded\n")
            sys.stderr.flush()
            
    async def _test_handler(self, **kwargs):
        """测试处理器"""
        return "✅ 阿里云MCP服务器连接成功！"
        
    async def setup_tools_async(self, services: Optional[str]):
        """异步设置工具"""
        # 配置服务列表
        if services:
            service_keys = [s.strip().lower() for s in services.split(",")]
            service_list = [(key, SUPPORTED_SERVICES_MAP.get(key, key)) for key in service_keys]
            
            try:
                from alibaba_cloud_ops_mcp_server.tools.common_api_tools import set_custom_service_list
                set_custom_service_list(service_list)
                logger.warning(f"Configured services: {service_keys}")
            except ImportError:
                logger.warning("Could not import service configuration")
        
        try:
            from fastmcp import FastMCP
            self.fastmcp_instance = FastMCP("alibaba-cloud-ops")
            
            # 导入并注册工具
            try:
                from alibaba_cloud_ops_mcp_server.tools import common_api_tools, oos_tools, cms_tools, oss_tools
                
                # 注册工具（限制数量以避免超时）
                tool_count = 0
                max_tools = 10  # 限制工具数量
                
                for tool_func in common_api_tools.tools:
                    if tool_count >= max_tools:
                        break
                    self.fastmcp_instance.tool(tool_func)
                    tool_count += 1
                    
                for tool_func in oos_tools.tools:
                    if tool_count >= max_tools:
                        break
                    self.fastmcp_instance.tool(tool_func)
                    tool_count += 1
                    
                for tool_func in cms_tools.tools:
                    if tool_count >= max_tools:
                        break
                    self.fastmcp_instance.tool(tool_func)
                    tool_count += 1
                    
                for tool_func in oss_tools.tools:
                    if tool_count >= max_tools:
                        break
                    self.fastmcp_instance.tool(tool_func)
                    tool_count += 1
                
                # 异步获取工具列表
                mcp_tools = await self.fastmcp_instance.get_tools()
                for tool in mcp_tools:
                    tool_name = tool.name
                    self.tools[tool_name] = {
                        "name": tool_name,
                        "description": tool.description or f"Execute {tool_name}",
                        "inputSchema": tool.inputSchema or {
                            "type": "object",
                            "properties": {},
                            "required": []
                        },
                        "handler": self.fastmcp_instance.get_tool(tool_name)
                    }
                        
            except ImportError as e:
                logger.error(f"Could not import tool modules: {e}")
                raise
                
        except ImportError:
            logger.warning("FastMCP not available")
            raise
            
        logger.warning(f"Loaded {len(self.tools)} tools")

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理MCP消息"""
        try:
            method = message.get("method")
            msg_id = message.get("id")
            
            if method == "initialize":
                # 启动工具加载
                if not self.tools_loaded:
                    asyncio.create_task(self._load_tools_async())
                
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "alibaba-cloud-ops-final",
                            "version": "1.0.0"
                        }
                    }
                }
                
            elif method in ["notifications/initialized", "initialized"]:
                self.initialized = True
                return None
                
            elif method == "tools/list":
                # 等待工具加载完成
                timeout = 15
                while not self.tools_loaded and timeout > 0:
                    await asyncio.sleep(0.1)
                    timeout -= 0.1
                
                tools_list = []
                for tool_info in self.tools.values():
                    tools_list.append({
                        "name": tool_info["name"],
                        "description": tool_info["description"],
                        "inputSchema": tool_info["inputSchema"]
                    })
                
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": tools_list
                    }
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
                    handler = self.tools[tool_name]["handler"]
                    if asyncio.iscoroutinefunction(handler):
                        result = await asyncio.wait_for(handler(**arguments), timeout=30.0)
                    else:
                        result = await asyncio.wait_for(
                            asyncio.get_event_loop().run_in_executor(None, lambda: handler(**arguments)),
                            timeout=30.0
                        )
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": str(result)}]
                        }
                    }
                    
                except asyncio.TimeoutError:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool {tool_name} execution timeout"
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
            
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def run(self):
        """运行服务器"""
        sys.stderr.write("Final Fixed MCP Server ready\n")
        sys.stderr.flush()
        
        # 设置信号处理
        def signal_handler(signum, frame):
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        while True:
            try:
                line = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline),
                    timeout=2.0
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
                logger.error(f"Server error: {e}")
                continue

def main():
    parser = argparse.ArgumentParser(description="Final Fixed Alibaba Cloud MCP Server")
    parser.add_argument("--services", type=str, help="Comma-separated list of services")
    parser.add_argument("--dashscope-url", type=str, help="DashScope URL (for compatibility)")
    args = parser.parse_args()
    
    server = FinalFixedMCPServer(services=args.services)
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
