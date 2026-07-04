from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_llm_service, validate_api_key
from app.schemas.openai import ChatCompletionRequest

router = APIRouter(prefix="/v1", tags=["chat"], dependencies=[Depends(validate_api_key)])


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest, llm_service=Depends(get_llm_service)):
    if request.stream:
        stream = llm_service.chat_completion_stream(request)
        return StreamingResponse(stream, media_type="text/event-stream")
    return await llm_service.chat_completion(request)
