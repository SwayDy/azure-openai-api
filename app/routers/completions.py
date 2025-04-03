from fastapi import APIRouter, Depends

from ..schemas.api import CompletionRequest, CompletionResponse
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
@router.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest,
    api_key: str = Depends(get_api_key)
):
    response = await inference_service.generate_completion(
        prompt=request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p
    )
    return response
