from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint. Returns service status."""
    return {
        "status": "ok",
        "service": "gridlane-engine",
        "version": "0.1.0",
    }
