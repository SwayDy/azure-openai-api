import json
import time
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from ..schemas.api import ChatCompletionRequest, CompletionResponse, ChatCompletionStreamResponse
from ..services.inference import InferenceService
from ..security import get_api_key
from ..config import get_settings

router = APIRouter()
settings = get_settings()
inference_service = InferenceService(
    azure_endpoint=settings.azure_endpoint,
    azure_api_key=settings.azure_api_key,
    model_name=settings.model_name
)

@router.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: str = Depends(get_api_key)
):  
    if request.stream:
        try:
            generator = inference_service.generate_chat_completion(
                messages=request.messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stream=request.stream
            )

            async def generate():
                async for chunk in generator:
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache"}
            )

        except Exception as e:
            error_data = {
                "error": {
                    "message": str(e),
                    "type": "api_error"
                }
            }
            if request.stream:
                return StreamingResponse(
                    iter([f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"]),
                    media_type="text/event-stream",
                    status_code=500
                )
    
    generator = inference_service.generate_chat_completion(
        messages=request.messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        stream=False,
    )
    return await generator.__anext__()
