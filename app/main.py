from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .routers import completions, chat
from .services.inference import InferenceService
from .config import get_settings

app = FastAPI(
    title="AI API",
    description="OpenAI API compatible interface for large language models",
    version="1.0.0"
)

app.include_router(completions.router)
app.include_router(chat.router)

settings = get_settings()
inference_service = InferenceService(
    azure_endpoint=settings.azure_endpoint,
    azure_api_key=settings.azure_api_key,
)

@app.get("/")
async def root():
    return {"message": "Welcome to AI API"}

# 添加新的路由
@app.get("/v1/models")
async def list_models():
    return await inference_service.list_models()

@app.get("/v1/models/{model_id}")
async def get_model(model_id: str):
    return await inference_service.get_model_info(model_id)

# 添加健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Production entry point for Gunicorn
    pass
