# oss_tools_fixed.py - 修复版本
import os
import alibabacloud_oss_v2 as oss
from alibaba_cloud_ops_mcp_server.alibabacloud.utils import get_credentials_from_header

from pydantic import Field
from alibabacloud_oss_v2 import Credentials
from alibabacloud_oss_v2.credentials import EnvironmentVariableCredentialsProvider
from alibabacloud_credentials.client import Client as CredClient


tools = []


class CredentialsProvider(EnvironmentVariableCredentialsProvider):
    def __init__(self) -> None:
        credentials = get_credentials_from_header()
        if credentials:
            access_key_id = credentials.get('AccessKeyId', None)
            access_key_secret = credentials.get('AccessKeySecret', None)
            session_token = credentials.get('SecurityToken', None)
        else:
            credentialsClient = CredClient()
            access_key_id = credentialsClient.get_credential().access_key_id
            access_key_secret = credentialsClient.get_credential().access_key_secret
            session_token = credentialsClient.get_credential().security_token

        self._credentials = Credentials(
            access_key_id, access_key_secret, session_token)

    def get_credentials(self) -> Credentials:
        return self._credentials


def create_client(region_id: str) -> oss.Client:
    credentials_provider = CredentialsProvider()
    cfg = oss.config.load_default()
    cfg.user_agent = 'alibaba-cloud-ops-mcp-server'
    cfg.credentials_provider = credentials_provider
    cfg.region = region_id
    return oss.Client(cfg)


@tools.append
def OSS_ListBuckets_Fixed(
    RegionId: str = 'cn-hangzhou',
    Prefix: str = None
):
    """列出指定区域的所有OSS存储空间。
    
    Args:
        RegionId: 阿里云区域ID，如cn-beijing, cn-hangzhou等
        Prefix: OSS存储桶名称前缀，可选
    """
    try:
        client = create_client(region_id=RegionId)
        paginator = client.list_buckets_paginator()
        results = []
        
        # 创建请求对象，只有在Prefix不为None时才传递
        if Prefix is not None:
            request = oss.ListBucketsRequest(prefix=Prefix)
        else:
            request = oss.ListBucketsRequest()
            
        for page in paginator.iter_page(request):
            for bucket in page.buckets:
                # 提取有用的存储桶信息
                bucket_info = {
                    'name': bucket.name,
                    'creation_date': str(bucket.creation_date) if bucket.creation_date else None,
                    'location': bucket.location,
                    'storage_class': bucket.storage_class,
                    'extranet_endpoint': bucket.extranet_endpoint,
                    'intranet_endpoint': bucket.intranet_endpoint
                }
                results.append(bucket_info)
        
        return results
    except Exception as e:
        return f"查询OSS存储桶失败: {str(e)}"


@tools.append
def OSS_ListObjects_Fixed(
    BucketName: str,
    RegionId: str = 'cn-hangzhou',
    Prefix: str = None
):
    """获取指定OSS存储空间中的所有文件信息。
    
    Args:
        BucketName: OSS存储桶名称
        RegionId: 阿里云区域ID
        Prefix: 对象名称前缀，可选
    """
    if not BucketName:
        return "存储桶名称不能为空"
        
    try:
        client = create_client(region_id=RegionId)
        paginator = client.list_objects_v2_paginator()
        results = []
        
        # 创建请求对象
        if Prefix is not None:
            request = oss.ListObjectsV2Request(bucket=BucketName, prefix=Prefix)
        else:
            request = oss.ListObjectsV2Request(bucket=BucketName)
            
        for page in paginator.iter_page(request):
            if page.contents:
                for obj in page.contents:
                    obj_info = {
                        'key': obj.key,
                        'size': obj.size,
                        'last_modified': str(obj.last_modified) if obj.last_modified else None,
                        'etag': obj.etag,
                        'storage_class': obj.storage_class
                    }
                    results.append(obj_info)
        
        return results
    except Exception as e:
        return f"查询OSS对象失败: {str(e)}"


@tools.append  
def OSS_PutBucket_Fixed(
    BucketName: str,
    RegionId: str = 'cn-hangzhou'
):
    """创建OSS存储空间。
    
    Args:
        BucketName: 存储桶名称
        RegionId: 阿里云区域ID
    """
    if not BucketName:
        return "存储桶名称不能为空"
        
    try:
        client = create_client(region_id=RegionId)
        request = oss.PutBucketRequest(bucket=BucketName)
        result = client.put_bucket(request)
        return f"存储桶 {BucketName} 创建成功"
    except Exception as e:
        return f"创建存储桶失败: {str(e)}"


@tools.append
def OSS_DeleteBucket_Fixed(
    BucketName: str,
    RegionId: str = 'cn-hangzhou'
):
    """删除OSS存储空间。
    
    Args:
        BucketName: 存储桶名称
        RegionId: 阿里云区域ID
    """
    if not BucketName:
        return "存储桶名称不能为空"
        
    try:
        client = create_client(region_id=RegionId)
        request = oss.DeleteBucketRequest(bucket=BucketName)
        result = client.delete_bucket(request)
        return f"存储桶 {BucketName} 删除成功"
    except Exception as e:
        return f"删除存储桶失败: {str(e)}"
