"""
User service business logic for user management operations.

The service translates repository models into API schema DTOs.
"""

from tasks_router.exceptions.custom_exceptions import ServiceException, UserNotFoundException, DatabaseOperationException
from tasks_router.schema.user_schema import User as UserDTO
from tasks_router.models.user_model import User as UserModel
from tasks_router.repositories.user_repo import UserRepository
from tasks_router.utils import convert_user_model_to_user_schema_dto

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        """Initialize the user service.

        Args:
            repository: User repository dependency.
        """
        self.repository = repository

    def get_user(self, username: str) -> UserDTO:
        """Return a user DTO by username.

        Args:
            username: Username to fetch from persistence.

        Returns:
            User DTO for API responses.

        Raises:
            UserNotFoundException: If no user matches the username.
            DatabaseOperationException: If repository access fails.
            ServiceException: If an unexpected service error occurs.
        """

        try:
            user = self.repository.get_by_id(username)
            return convert_user_model_to_user_schema_dto(user)
        except UserNotFoundException:
            raise
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error retrieving user with username {username}: {str(e)}") from e

    def create(self, user: UserDTO) -> UserDTO:
        """Create and return a user DTO.

        Args:
            user: Input user DTO from the API layer.

        Returns:
            Persisted user DTO for API responses.

        Raises:
            DatabaseOperationException: If repository persistence fails.
            ServiceException: If an unexpected service error occurs.
        """

        new_user_data = user.model_dump(exclude_unset=True)
        new_user = UserModel(**new_user_data)

        try:
            created_user = self.repository.create(new_user)
            return convert_user_model_to_user_schema_dto(created_user)
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error creating user with username {user.username}: {str(e)}") from e
