# AI API

这是一个兼容OpenAI API格式的大模型接口项目，基于FastAPI框架构建，支持Azure AI服务集成。

## 功能特点

- 完全兼容OpenAI API格式
- 支持文本补全和对话补全
- 异步处理请求
- API密钥认证
- Prometheus监控集成
- Docker容器化部署

## 架构设计

```mermaid
graph TD
    A[客户端] --> B[FastAPI应用]
    B --> C{路由层}
    C --> D[/v1/chat/completions POST]
    C --> E[/v1/models GET]
    D --> F[InferenceService]
    E --> F
    F --> G[Azure AI SDK]
    H[环境变量] --> I[Config]
    I --> F
    J[Docker容器] --> B
    J --> K[Gunicorn/Uvicorn]
```

## 快速开始

### 本地运行
1. 克隆项目
```bash
git clone https://github.com/your-repo/azure-openai-api.git
cd azure-openai-api
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 创建.env配置文件：
```ini
AZURE_ENDPOINT=your-azure-endpoint
AZURE_API_KEY=your-api-key
API_KEY=${API_KEY:-your-local-api-key}
HOST=0.0.0.0
PORT=8000
```

4. 启动服务：
```bash
uvicorn app.main:app --reload
```

### Docker部署
```bash
docker-compose -f docker-compose.yml --env-file .env up --build
```

## API端点

- POST /v1/completions - 文本补全
- POST /v1/chat/completions - 对话补全
- GET  /v1/models - 获取可用模型列表
- GET  /health - 健康检查端点
- GET  /metrics - Prometheus监控指标

## 配置说明

在.env文件中设置以下变量：

| 变量名称         | 说明                         | 示例值                                  |
|------------------|------------------------------|----------------------------------------|
| AZURE_ENDPOINT   | Azure AI服务终结点           | https://your-endpoint.openai.azure.com |
| AZURE_API_KEY    | Azure API密钥                | your-api-key                           |
| API_KEY          | 本地API访问密钥              | your-local-key                         |
| HOST             | 服务监听地址                 | 0.0.0.0                                |
| PORT             | 服务监听端口                 | 8000                                   |

## 监控与运维

### 健康检查
```bash
curl http://localhost:8000/health
```

## 使用示例

### 基础请求
```python
import requests

API_URL = "http://localhost:8000/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('API_KEY')}"
}
data = {
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
}

response = requests.post(API_URL, headers=headers, json=data)
print(response.json())
```

### 流式响应
```python
import requests

API_URL = "http://localhost:8000/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('API_KEY')}"
}
data = {
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100,
    "stream": True
}

with requests.post(API_URL, headers=headers, json=data, stream=True) as response:
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
```

## 开发指南

### 运行测试
```bash
pytest test.py
```

### 代码规范
- 遵循PEP8规范
- 使用类型注解
- 重要函数添加docstring

### 构建Docker镜像
```bash
docker build -t ai-api:latest .
```

### 贡献代码
1. Fork项目仓库
2. 创建特性分支
3. 提交Pull Request
