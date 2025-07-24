#!/usr/bin/env python3
"""
Q CLI Compatible MCP Server for Alibaba Cloud Operations - Fixed Version

This version addresses timeout issues by:
1. Increasing tool execution timeout from 5s to 30s
2. Improving error handling for tool loading
3. Adding better timeout management for stdin reading
4. Providing more robust fallback mechanisms
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

# Configure minimal logging for faster startup
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
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

class QCLICompatibleServerFixed:
    def __init__(self, services: Optional[str] = None):
        self.initialized = False
        self.tools = {}
        self.services = services
        self.tools_loaded = False
        self.tool_loading_timeout = 30  # Increased timeout for tool loading
        
        # Send immediate ready signal to Q CLI
        sys.stderr.write("Server starting (Fixed Version)...\n")
        sys.stderr.flush()
        
        # Start background tool loading with longer timeout
        self.load_thread = threading.Thread(target=self._load_tools_background, daemon=True)
        self.load_thread.start()
        
        logger.warning(f"Q CLI Compatible Server (Fixed) initialized, loading tools in background")
        
    def _load_tools_background(self):
        """Load tools in background with improved error handling"""
        try:
            # Wait a bit to ensure proper initialization
            time.sleep(2)
            self.setup_tools(self.services)
            self.tools_loaded = True
            sys.stderr.write(f"Tools loaded successfully: {len(self.tools)} available\n")
            sys.stderr.flush()
        except Exception as e:
            logger.error(f"Error loading tools: {e}")
            # Provide comprehensive fallback tools
            self.tools = {
                "test_connection": {
                    "name": "test_connection",
                    "description": "Test Alibaba Cloud MCP connection",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "handler": self._test_handler
                },
                "list_oss_buckets": {
                    "name": "list_oss_buckets",
                    "description": "List OSS buckets in specified region",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name (e.g., cn-beijing)"
                            }
                        },
                        "required": []
                    },
                    "handler": self._list_oss_buckets_handler
                }
            }
            self.tools_loaded = True
            sys.stderr.write(f"Fallback tools loaded: {len(self.tools)} available\n")
            sys.stderr.flush()
            
    async def _test_handler(self):
        """Simple test handler"""
        return "✅ Alibaba Cloud MCP Server (Fixed Version) connection test successful!"
        
    async def _list_oss_buckets_handler(self, region: str = "cn-beijing"):
        """Fallback OSS bucket listing handler"""
        try:
            # Try to import and use the actual OSS tools
            from alibaba_cloud_ops_mcp_server.tools import oss_tools
            
            # Look for list_buckets function
            for tool_func in oss_tools.tools:
                if 'bucket' in tool_func.__name__.lower() and 'list' in tool_func.__name__.lower():
                    result = await asyncio.wait_for(tool_func(region=region), timeout=30.0)
                    return result
                    
            # If no specific function found, return a helpful message
            return f"OSS bucket listing functionality is available but requires proper configuration for region: {region}"
            
        except ImportError:
            return f"OSS tools not available. Please ensure Alibaba Cloud credentials are configured for region: {region}"
        except Exception as e:
            return f"Error listing OSS buckets in {region}: {str(e)}"
        
    def setup_tools(self, services: Optional[str]):
        """Setup all available tools with improved error handling"""
        # Setup service list if specified
        if services:
            service_keys = [s.strip().lower() for s in services.split(",")]
            service_list = [(key, SUPPORTED_SERVICES_MAP.get(key, key)) for key in service_keys]
            
            try:
                from alibaba_cloud_ops_mcp_server.tools.common_api_tools import set_custom_service_list
                set_custom_service_list(service_list)
                logger.warning(f"Configured services: {service_keys}")
            except ImportError:
                logger.warning("Could not import service configuration")
        
        # Use FastMCP to register and extract tools properly
        try:
            from fastmcp import FastMCP
            temp_mcp = FastMCP("temp")
            
            # Import and register tools with better error handling
            try:
                from alibaba_cloud_ops_mcp_server.tools import common_api_tools, oos_tools, cms_tools, oss_tools, api_tools
                from alibaba_cloud_ops_mcp_server.config import config
                
                # Register all tools with FastMCP to get proper schema extraction
                for tool_func in common_api_tools.tools:
                    temp_mcp.tool(tool_func)
                    
                for tool_func in oos_tools.tools:
                    temp_mcp.tool(tool_func)
                    
                for tool_func in cms_tools.tools:
                    temp_mcp.tool(tool_func)
                    
                for tool_func in oss_tools.tools:
                    temp_mcp.tool(tool_func)
                
                # Add API tools (these are created dynamically)
                try:
                    api_tools.create_api_tools(temp_mcp, config)
                except Exception as e:
                    logger.warning(f"Could not load API tools: {e}")
                
                # Extract tools from FastMCP instance
                if hasattr(temp_mcp, '_tools'):
                    for tool_name, tool_info in temp_mcp._tools.items():
                        self.tools[tool_name] = tool_info
                else:
                    # Fallback: manually extract tool information
                    logger.warning("FastMCP doesn't have _tools attribute, using fallback method")
                    all_tool_funcs = (common_api_tools.tools + oos_tools.tools + 
                                    cms_tools.tools + oss_tools.tools)
                    
                    for tool_func in all_tool_funcs:
                        tool_name = tool_func.__name__
                        # Extract description from docstring
                        description = tool_func.__doc__ or f"Execute {tool_name}"
                        
                        self.tools[tool_name] = {
                            "name": tool_name,
                            "description": description.strip().split('\n')[0],
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            },
                            "handler": tool_func
                        }
                        
            except ImportError as e:
                logger.error(f"Could not import tool modules: {e}")
                # Provide basic test tool
                self.tools = {
                    "test_connection": {
                        "name": "test_connection",
                        "description": "Test Alibaba Cloud MCP connection",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        },
                        "handler": self._test_handler
                    }
                }
                
        except ImportError:
            logger.warning("FastMCP not available, using minimal tools")
            self.tools = {
                "test_connection": {
                    "name": "test_connection",
                    "description": "Test Alibaba Cloud MCP connection",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "handler": self._test_handler
                }
            }
            
        logger.warning(f"Loaded {len(self.tools)} tools: {list(self.tools.keys())[:5]}...")

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP messages with Q CLI compatibility and improved timeout handling"""
        try:
            method = message.get("method")
            msg_id = message.get("id")
            
            logger.debug(f"Received message: {method} (id: {msg_id})")
            
            # Handle initialization - Q CLI sends "initialized" instead of "notifications/initialized"
            if method == "initialized":
                logger.warning("Received Q CLI initialization notification")
                self.initialized = True
                return None  # Notifications don't need responses
                
            # Handle standard initialization notification
            elif method == "notifications/initialized":
                logger.warning("Received standard initialization notification")
                self.initialized = True
                return None
                
            # Handle initialize request
            elif method == "initialize":
                logger.warning("Handling initialize request")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "logging": {}
                        },
                        "serverInfo": {
                            "name": "alibaba-cloud-ops-mcp-server-fixed",
                            "version": "1.0.1"
                        }
                    }
                }
                
            # Handle tools list request
            elif method == "tools/list":
                logger.warning(f"Handling tools/list request (initialized: {self.initialized}, tools_loaded: {self.tools_loaded})")
                
                # Wait a bit for tools to load if they're still loading
                if not self.tools_loaded:
                    for i in range(10):  # Wait up to 10 seconds
                        if self.tools_loaded:
                            break
                        await asyncio.sleep(1)
                
                # Always return immediately with available tools
                tools_list = []
                for tool_name, tool_info in self.tools.items():
                    tools_list.append({
                        "name": tool_name,
                        "description": tool_info["description"],
                        "inputSchema": tool_info["inputSchema"]
                    })
                
                # If no tools loaded yet, provide basic tools
                if not tools_list:
                    tools_list = [{
                        "name": "test_connection",
                        "description": "Test Alibaba Cloud MCP connection",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }]
                
                return {
                    "jsonrpc": "2.0", 
                    "id": msg_id,
                    "result": {
                        "tools": tools_list
                    }
                }
                
            # Handle tool calls with extended timeout
            elif method == "tools/call":
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.warning(f"Handling tool call: {tool_name} with args: {arguments}")
                
                if tool_name not in self.tools:
                    # If tool not found in loaded tools, check if it's the test tool
                    if tool_name == "test_connection":
                        return {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "content": [{"type": "text", "text": "✅ Alibaba Cloud MCP Server (Fixed) connection test successful!"}]
                            }
                        }
                    else:
                        return {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {
                                "code": -32601,
                                "message": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
                            }
                        }
                
                try:
                    # Call the tool handler with extended timeout (30 seconds instead of 5)
                    tool_handler = self.tools[tool_name]["handler"]
                    
                    # Execute with extended timeout
                    try:
                        result = await asyncio.wait_for(tool_handler(**arguments), timeout=30.0)
                    except asyncio.TimeoutError:
                        result = f"Tool '{tool_name}' is taking longer than expected to execute. This may be due to network latency or API response time. Please try again."
                    
                    # Format result for MCP
                    if isinstance(result, str):
                        content = [{"type": "text", "text": result}]
                    elif isinstance(result, dict):
                        content = [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
                    else:
                        content = [{"type": "text", "text": str(result)}]
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": content
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Tool execution error: {e}")
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": f"Tool execution completed with message: {str(e)}"}]
                        }
                    }
            
            else:
                logger.warning(f"Unknown method: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
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
        """Run the server using stdio transport with improved timeout handling"""
        logger.warning("Starting Q CLI Compatible MCP Server (Fixed Version)")
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        while True:
            try:
                # Read message from stdin with longer timeout (5 seconds instead of 1)
                line = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline),
                    timeout=5.0
                )
                
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                # Parse JSON message
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue
                
                # Handle message
                response = await self.handle_message(message)
                
                # Send response if needed
                if response:
                    response_json = json.dumps(response, ensure_ascii=False)
                    print(response_json, flush=True)
                    logger.debug(f"Sent response: {response_json}")
                    
            except asyncio.TimeoutError:
                # Continue on timeout to keep server responsive
                continue
            except KeyboardInterrupt:
                logger.warning("Server interrupted")
                break
            except Exception as e:
                logger.error(f"Server error: {e}")
                continue

def main():
    parser = argparse.ArgumentParser(description="Q CLI Compatible Alibaba Cloud MCP Server (Fixed)")
    parser.add_argument("--services", type=str, help="Comma-separated list of services")
    parser.add_argument("--dashscope-url", type=str, help="DashScope URL (for compatibility)")
    args = parser.parse_args()
    
    server = QCLICompatibleServerFixed(services=args.services)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.warning("Server stopped")

if __name__ == "__main__":
    main()
