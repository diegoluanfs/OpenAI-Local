from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_llm_service, validate_api_key
from app.schemas.openai import CompletionRequest

router = APIRouter(prefix="/v1", tags=["completions"], dependencies=[Depends(validate_api_key)])


@router.post("/completions")
async def completions(request: CompletionRequest, llm_service=Depends(get_llm_service)):
    if request.stream:
        stream = llm_service.completion_stream(request)
        return StreamingResponse(stream, media_type="text/event-stream")
    return await llm_service.completion(request)
