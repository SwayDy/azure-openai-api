from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = Field(default=2048)
    stop: Optional[Union[str, List[str]]] = Field(default=None)
    stream: bool = Field(default=False)
    temperature: float = Field(default=0.6)
    top_p: float = Field(default=0.95)
    
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: int = Field(default=2048)
    stop: Optional[Union[str, List[str]]] = Field(default=None)
    stream: bool = Field(default=False)
    temperature: float = Field(default=0.6)
    top_p: float = Field(default=0.95)
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('messages cannot be empty')
        if not all(m.role in ['system', 'user', 'assistant'] for m in v):
            raise ValueError('invalid role in messages')
        return v

class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[dict]
    usage: dict

class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class StreamChoice(BaseModel):
    delta: DeltaMessage
    index: int = 0
    finish_reason: Optional[str] = None

class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]

class ModelPermission(BaseModel):
    id: str
    object: str = "model_permission"
    created: int = 1677649963
    allow_create_engine: bool = False
    allow_sampling: bool = True
    allow_logprobs: bool = True
    allow_search_indices: bool = False

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677649963
    owned_by: str = "azure-ai"
    root: str = "azure-ai"
    parent: str = None
    permission: List[ModelPermission] = []
    max_tokens: int = 32768
    backend: str = "azure-ai"

class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

class ErrorResponse(BaseModel):
    message: str
    type: str
    param: Optional[str] = None
    code: str
