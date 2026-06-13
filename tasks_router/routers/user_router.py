"""
User management API endpoints for retrieving and creating users.
"""

import structlog
from fastapi import APIRouter, Depends, status, HTTPException

from tasks_router.exceptions.custom_exceptions import UserNotFoundException, DatabaseOperationException, ServiceException
from tasks_router.services.user_service import UserService
from tasks_router.schema.user_schema import User, UserCreate
from tasks_router.dependencies import get_user_services

router: APIRouter = APIRouter(prefix="/users", tags=["Users"])
logger = structlog.get_logger(__name__)


@router.get(
        "/{username}",
        response_model=User,
        status_code=status.HTTP_200_OK
    )
def get_user(
    username: str,
    user_services: UserService = Depends(get_user_services)
) -> User:
    """Retrieve a user by username.

    Args:
        username (str): Username path parameter used to look up the user.
        user_services (UserService): User service dependency used to fetch user data.

    Returns:
        User: The requested user's response schema.

    Raises:
        HTTPException: 404 if the user cannot be found.
        HTTPException: 500 if a database operation fails.
        HTTPException: 400 if a service-layer validation or business rule fails.

    Status Codes:
        200: User retrieved successfully.
        404: User not found.
    """

    try:
        logger.info("Retrieving user", username=username)
        user: User = user_services.get_user(username)
        logger.info("User retrieved", username=username)
        return user
    except UserNotFoundException:
        logger.warning("User not found", username=username)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except DatabaseOperationException as e:
        logger.error("DB Ops error while retrieving user", username=username, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        logger.error("Service error while retrieving user", username=username, error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while retrieving user", username=username)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while retrieving the user") from e

@router.post(
        "/",
        response_model=User,
        status_code=status.HTTP_201_CREATED
    )
def create_user(
    user: UserCreate,
    user_services: UserService = Depends(get_user_services)
    ) -> User:
    """Create a new user.

    Args:
        user (UserCreate): Payload containing username and display name.
        user_services (UserService): User service dependency used to persist the new user.

    Returns:
        User: The created user's response schema.

    Raises:
        HTTPException: 500 if a database operation fails.
        HTTPException: 400 if a service-layer validation or business rule fails.

    Status Codes:
        201: User created successfully.
    """

    try:
        logger.info("Creating new user", username=user.username)
        created_user = user_services.create(user)
        logger.info("User created", username=created_user.username)
        return created_user
    except DatabaseOperationException as e:
        logger.error("DB Ops error while creating user", username=user.username, error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        logger.error("Service error while creating user", username=user.username, error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while creating user", username=user.username)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while creating the user") from e
