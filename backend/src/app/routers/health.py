from fastapi import APIRouter

from app.core.config import settings
from app.core.redis import ping_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    redis_ok = await ping_redis()

    status = "healthy" if redis_ok else "degraded"

    return {
        "status": status,
        "version": settings.version,
        "redis": "connected" if redis_ok else "unavailable",
    }
