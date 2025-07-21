#!/usr/bin/env python3
"""
简单的FastMCP测试服务器
"""
import sys
from mcp.server.fastmcp import FastMCP

# 创建FastMCP服务器
app = FastMCP()

@app.tool()
def hello_world() -> str:
    """简单的测试工具"""
    return "Hello from Alibaba Cloud FastMCP!"

def run_server():
    """运行FastMCP服务器"""
    print("Starting Simple FastMCP server...", file=sys.stderr)
    print("Server is ready to accept connections.", file=sys.stderr)
    app.run()

if __name__ == "__main__":
    run_server()
