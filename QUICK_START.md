# Quick Start Guide

## 🎉 Repository Successfully Uploaded!

Your Alibaba Cloud Operations MCP Server with Q CLI compatibility improvements has been successfully uploaded to:
**https://github.com/RadiumGu/alicloud-ops-mcp**

## 📁 What's Included

- **Original Alibaba Cloud MCP Server**: Complete source code in `alibaba_cloud_ops_mcp_server/`
- **Q CLI Compatible Version**: `qcli_compatible_server_fixed.py` - Enhanced for Amazon Q CLI
- **Stable Working Version**: `working_server.py` - Production-ready implementation
- **Comprehensive Documentation**: 
  - `IMPROVEMENTS.md` - Overview of all improvements
  - `QCLI_COMPATIBILITY_FIX.md` - Technical details of fixes
  - Original README files in English and Chinese

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/RadiumGu/alicloud-ops-mcp.git
cd alicloud-ops-mcp
```

### 2. Install Dependencies
```bash
pip install fastmcp alibabacloud-ecs20140526 alibabacloud-oss-sdk2 alibabacloud-cms20190101
```

### 3. Configure Credentials
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
export ALIBABA_CLOUD_REGION="cn-beijing"
```

### 4. Run the Server
```bash
# Use the Q CLI compatible version
python qcli_compatible_server_fixed.py

# Or use the stable working version
python working_server.py
```

### 5. Integrate with Amazon Q CLI
```bash
q configure mcp add alibaba-cloud-ops /path/to/qcli_compatible_server_fixed.py
```

## 🔧 Key Features

- **ECS Management**: List, start, stop, and monitor EC2 instances
- **OSS Operations**: Bucket and object management
- **OOS Automation**: Orchestration and automation workflows
- **CMS Monitoring**: Cloud monitoring and alerting
- **Enhanced Q CLI Compatibility**: Optimized for Amazon Q CLI integration

## 📚 Documentation

- Read `IMPROVEMENTS.md` for detailed improvement information
- Check `QCLI_COMPATIBILITY_FIX.md` for technical implementation details
- Refer to original README files for basic usage

## 🤝 Contributing

Feel free to submit issues and pull requests to improve the server further!

---
**Repository**: https://github.com/RadiumGu/alicloud-ops-mcp
**Status**: ✅ Successfully uploaded and ready to use!
