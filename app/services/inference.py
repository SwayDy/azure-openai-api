import time
import uuid
import json
import asyncio
import logging

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

from typing import List, Dict, AsyncGenerator, Optional, Union
from ..schemas.api import ChatMessage

class InferenceService:
    def __init__(self, azure_endpoint: str, azure_api_key: str):
        self.logger = logging.getLogger(__name__)
        self.client = ChatCompletionsClient(
            endpoint=azure_endpoint,
            credential=AzureKeyCredential(azure_api_key)
        )
        
        # 预定义的模型列表数据（后续可替换为Azure API调用）
        self.available_models = [
            {
                "id": "DeepSeek-R1",
                "object": "model",
                "owned_by": "azure-ai",
                "permission": [
                    {"id": f"modelperm-{uuid.uuid4()}", "object": "model_permission"}
                ]
            },
            {
                "id": "DeepSeek-V3",
                "object": "model",
                "owned_by": "azure-ai",
                "permission": [
                    {"id": f"modelperm-{uuid.uuid4()}", "object": "model_permission"}
                ]
            },
        ]

    def _convert_messages(self, messages: List[ChatMessage]):
        """转换消息格式为Azure SDK格式"""
        azure_messages = []
        for msg in messages:
            if msg.role == "system":
                azure_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                azure_messages.append(UserMessage(content=msg.content))
            elif msg.role == "assistant":
                azure_messages.append(AssistantMessage(content=msg.content))
        return azure_messages

    async def generate_chat_completion(
            self, 
            model: str,
            messages: List[ChatMessage],
            max_tokens: int = 2048,
            stop: Optional[Union[str, List[str]]] = None,
            stream: bool = False,
            temperature: float = 0.6,
            top_p: float = 0.95,
        ) -> AsyncGenerator[str, None]:
        try:
            azure_messages = self._convert_messages(messages)
            
            created = int(time.time())
            response_id = f"chatcmpl-{uuid.uuid4()}"
            
            if stream:
                # 将同步生成器转换为异步生成器
                sync_generator = await asyncio.to_thread(
                    self.client.complete,
                    model=model,
                    messages=azure_messages,
                    max_tokens=max_tokens,
                    stop = stop,
                    stream=True,
                    temperature=temperature,
                    top_p=top_p,
                )
                
                # 异步迭代包装器
                async def async_wrapper():
                    for chunk in sync_generator:
                        yield chunk
                        await asyncio.sleep(0)  # 释放事件循环
                
                async for chunk in async_wrapper():  # 流式响应处理
                    # 显式提取原始值并转换为基本类型
                    chunk_data = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "content": str(chunk.choices[0].delta.content) if chunk.choices and chunk.choices[0].delta.content else "",
                            },
                            "finish_reason": str(chunk.choices[0].finish_reason) if chunk.choices else None
                        }],
                        "usage": {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens
                        } if chunk.usage else {}
                    }
                    yield chunk_data
                    await asyncio.sleep(0)  # 释放事件循环
            else:
                # 非流式响应处理
                response = await asyncio.to_thread(
                    self.client.complete,
                    model=model,
                    messages=azure_messages,
                    max_tokens=max_tokens,
                    stop = stop,
                    stream=False,
                    temperature=temperature,
                    top_p=top_p,
                )
                # 构造符合OpenAI格式的响应
                completion_response = {
                    "id": response_id,
                    "object": "chat.completion",
                    "created": created,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": str(response.choices[0].message.content) if response.choices else ""
                        },
                        "finish_reason": str(response.choices[0].finish_reason) if response.choices else None
                    }],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    } if response.usage else {}
                }
                yield completion_response
        except Exception as e:
            self.logger.error(f"API请求失败: {str(e)}")
            error_data = {
                "error": {
                    "message": f"模型服务错误: {str(e)}",
                    "type": "api_error",
                    "code": 503
                }
            }
            if stream:
                # 流式错误响应
                yield {
                    "error": error_data,
                    "id": response_id,
                    "model": self.model_name
                }
            else:
                # 非流式错误响应
                raise ValueError(json.dumps(error_data)) from e

    async def list_models(self) -> dict:
        """获取可用模型列表（符合OpenAI格式）"""
        return {
            "object": "list",
            "data": self.available_models
        }

    async def get_model_info(self, model_id: str) -> dict:
        """获取单个模型详情"""
        model = next((m for m in self.available_models if m["id"] == model_id), None)
        if not model:
            raise ValueError(f"Model {model_id} not found")
            
        return {
            **model,
            "max_tokens": 32768,  # 根据实际模型能力调整
            "backend": "azure-ai",
            "status": "active"
        }
