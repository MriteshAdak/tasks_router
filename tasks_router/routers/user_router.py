"""
User management API endpoints for retrieving and creating users.
"""

from fastapi import APIRouter, Depends, status, HTTPException

from tasks_router.exceptions.custom_exceptions import UserNotFoundException, DatabaseOperationException, ServiceException
from tasks_router.services.user_service import UserService
from tasks_router.schema.user_schema import User
from tasks_router.dependencies import get_user_services

router: APIRouter = APIRouter(prefix="/users", tags=["Users"])


@router.get(
        "/{username}",
        response_model=User,
        status_code=status.HTTP_200_OK)
def get_user(
    username: str,
    user_services: UserService = Depends(get_user_services)
    ) -> User:
    """Fetch a user by username.

    Args:
        username: Username from route path.
        user_services: Injected user service dependency.

    Returns:
        User DTO for API response.

    Raises:
        HTTPException: If lookup operations fail.
    """

    try:
        user: User = user_services.get_user(username)
        return user
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while retrieving the user") from e

@router.post(
        "/",
        response_model=User,
        status_code=status.HTTP_201_CREATED
    )
def create_user(
    user: User,
    user_services: UserService = Depends(get_user_services)
    ) -> User:
    """Create a new user.

    Args:
        user: User payload from request body.
        user_services: Injected user service dependency.

    Returns:
        Persisted user DTO.

    Raises:
        HTTPException: If create operations fail.
    """

    try:
        return user_services.create(user)
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while creating the user") from e
