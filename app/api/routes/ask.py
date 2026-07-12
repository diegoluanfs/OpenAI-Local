from fastapi import APIRouter, Depends

from app.api.dependencies import get_llm_service, validate_api_key
from app.schemas.openai import AskRequest, AskResponse

router = APIRouter(prefix="", tags=["public"], dependencies=[Depends(validate_api_key)])


@router.post("/ask")
async def ask(request: AskRequest, llm_service=Depends(get_llm_service)) -> AskResponse:
    return await llm_service.ask(request)
