from fastapi import APIRouter, Depends

from app.api.dependencies import get_health_service

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(health_service=Depends(get_health_service)):
    return await health_service.status()


@router.get("/health/live")
async def health_live(health_service=Depends(get_health_service)):
    return await health_service.liveness()


@router.get("/health/ready")
async def health_ready(health_service=Depends(get_health_service)):
    return await health_service.readiness()
