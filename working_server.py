#!/usr/bin/env python3
"""
Working MCP Server - Follows exact MCP protocol specification
"""

import json
import sys
import signal
import os

class WorkingMCPServer:
    def __init__(self):
        self.initialized = False
        
    def handle_message(self, message):
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
                        "name": "alibaba-cloud-ops-working",
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
                    "tools": [
                        {
                            "name": "alibaba_cloud_test",
                            "description": "Test Alibaba Cloud MCP connection",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {
                                        "type": "string",
                                        "description": "Test message"
                                    }
                                },
                                "required": []
                            }
                        }
                    ]
                }
            }
            
        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            
            if tool_name == "alibaba_cloud_test":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "✅ Alibaba Cloud MCP Server is working! Connection successful."
                            }
                        ]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }

def main():
    server = WorkingMCPServer()
    
    # Handle SIGTERM gracefully
    def signal_handler(signum, frame):
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            try:
                message = json.loads(line)
                response = server.handle_message(message)
                
                if response:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id") if 'message' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
