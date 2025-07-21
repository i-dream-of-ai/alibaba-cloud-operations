#!/usr/bin/env python3
"""
安全的OSS测试脚本 - 从环境变量或.env文件读取凭证
"""
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, 'alibaba_cloud_ops_mcp_server')

def load_env_file():
    """从.env文件加载环境变量"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def test_oss_buckets():
    """测试OSS存储桶列表功能"""
    # 加载环境变量
    load_env_file()
    
    # 检查必要的环境变量
    required_vars = ['ALIBABA_CLOUD_ACCESS_KEY_ID', 'ALIBABA_CLOUD_ACCESS_KEY_SECRET']
    for var in required_vars:
        if not os.environ.get(var):
            print(f"❌ 环境变量 {var} 未设置")
            return
    
    print('正在查询阿里云OSS存储桶...')
    print('=' * 50)
    
    try:
        from tools import oss_tools
        
        # 使用修复后的OSS工具
        list_buckets_func = oss_tools.tools[0]
        result = list_buckets_func(RegionId='cn-hangzhou')
        
        if isinstance(result, list) and result:
            print(f'✅ 找到 {len(result)} 个OSS存储桶:')
            print()
            
            # 按region分组显示
            regions = {}
            for bucket in result:
                if isinstance(bucket, dict):
                    location = bucket.get('location', '未知')
                    if location not in regions:
                        regions[location] = []
                    regions[location].append(bucket)
            
            total_buckets = 0
            for region, buckets in sorted(regions.items()):
                print(f'📍 Region: {region}')
                print('-' * 40)
                for i, bucket in enumerate(buckets, 1):
                    total_buckets += 1
                    print(f'{total_buckets}. 存储桶名称: {bucket.get("name", "未知")}')
                    print(f'   创建时间: {bucket.get("creation_date", "未知")}')
                    print(f'   存储类型: {bucket.get("storage_class", "未知")}')
                    print(f'   外网端点: {bucket.get("extranet_endpoint", "未知")}')
                    print()
                print()
                
            print(f'📊 总计: {total_buckets} 个OSS存储桶分布在 {len(regions)} 个region中')
                
        elif isinstance(result, str):
            print(f'❌ {result}')
        else:
            print('❌ 没有找到OSS存储桶')
            
    except Exception as e:
        print(f'❌ 查询失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_oss_buckets()
