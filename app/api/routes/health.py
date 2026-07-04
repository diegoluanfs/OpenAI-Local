from fastapi import APIRouter, Depends

from app.api.dependencies import get_health_service

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(health_service=Depends(get_health_service)):
    return await health_service.status()
