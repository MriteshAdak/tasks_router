"""
System endpoints for health checks and root welcome message.
"""

import structlog
from fastapi import APIRouter, status

router: APIRouter = APIRouter(tags=["System"])
logger = structlog.get_logger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Return service health status.

    Returns:
        dict[str, str]: A simple JSON payload indicating service health.

    Status Codes:
        200: Service is healthy.
    """
    logger.debug("system.health_check")
    return {
        "service": "tasks-api",
        "status": "healthy"
        }

@router.get("/", status_code=status.HTTP_200_OK)
async def root() -> dict[str, str | dict[str, str]]:
    """Return a welcome message and available API endpoints.

    Returns:
        dict[str, str | dict[str, str]]: A map containing a welcome message and route descriptions.

    Status Codes:
        200: Request successful.
    """
    logger.debug("system.root")
    return {
        "message": "Welcome to the Tasks API!",
        "endpoints": {
            "/tasks": "Manage tasks (CRUD operations)",
            "/health": "Check the health status of the service",
            "/docs": "API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)"
        }
    }
