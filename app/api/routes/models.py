from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_llm_service, validate_api_key
from app.schemas.openai import PullModelRequest, SetDefaultModelRequest

router = APIRouter(prefix="/v1/models", tags=["models"], dependencies=[Depends(validate_api_key)])


@router.get("")
async def list_models(llm_service=Depends(get_llm_service)):
    models = await llm_service.list_models()
    data = [
        {
            "id": model.get("name", ""),
            "object": "model",
            "created": 0,
            "owned_by": "ollama",
        }
        for model in models
    ]
    return {"object": "list", "data": data}


@router.get("/default")
async def get_default_model(llm_service=Depends(get_llm_service)):
    return {"model": await llm_service.get_default_model()}


@router.put("/default")
async def set_default_model(request: SetDefaultModelRequest, llm_service=Depends(get_llm_service)):
    if not await llm_service.ensure_model_available(request.model):
        raise HTTPException(status_code=404, detail=f"Model '{request.model}' is not installed")
    model = await llm_service.set_default_model(request.model)
    return {"model": model}


@router.post("/pull")
async def pull_model(request: PullModelRequest, llm_service=Depends(get_llm_service)):
    result = await llm_service.pull_model(request.model)
    return {"status": "ok", "details": result}


@router.get("/status")
async def model_status(model: str, llm_service=Depends(get_llm_service)):
    return {"model": model, "available": await llm_service.ensure_model_available(model), "provider": "ollama"}
