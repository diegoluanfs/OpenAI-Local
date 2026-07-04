from fastapi import APIRouter, Depends

from app.api.dependencies import get_llm_service, validate_api_key
from app.schemas.openai import EmbeddingRequest

router = APIRouter(prefix="/v1", tags=["embeddings"], dependencies=[Depends(validate_api_key)])


@router.post("/embeddings")
async def embeddings(request: EmbeddingRequest, llm_service=Depends(get_llm_service)):
    return await llm_service.embeddings(request)
