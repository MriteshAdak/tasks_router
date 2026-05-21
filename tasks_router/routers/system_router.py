"""
System endpoints for health checks and root welcome message.
"""

from fastapi import APIRouter, status

router: APIRouter = APIRouter(tags=["System"])

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Return a basic service health payload.

    Returns:
        Health metadata for uptime probes.
    """
    return {
        "service": "tasks-api",
        "status": "healthy"
        }

@router.get("/", status_code=status.HTTP_200_OK)
async def root() -> dict[str, str | dict[str, str]]:
    """Return a welcome payload with discoverable endpoints.

    Returns:
        API summary and endpoint descriptions for first-time users.
    """
    return {
        "message": "Welcome to the Tasks API!",
        "endpoints": {
            "/tasks": "Manage tasks (CRUD operations)",
            "/health": "Check the health status of the service",
            "/docs": "API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)"
        }
    }
