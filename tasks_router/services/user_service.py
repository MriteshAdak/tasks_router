"""
UserService class that provides business logic for user management operations.
This module defines the UserService class, which interacts with the UserRepository to perform CRUD operations on User entities. The UserService class also handles the conversion of UserModel instances to UserSchemas for API responses.
"""
import structlog

from tasks_router.exceptions.custom_exceptions import ServiceException, UserNotFoundException, DatabaseOperationException
from tasks_router.schema.user_schema import User as UserDTO, UserCreate
from tasks_router.models.user_model import User as UserModel
from tasks_router.repositories.user_repo import UserRepository
from tasks_router.utils import convert_user_model_to_user_schema_dto

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        """Initialize the UserService with a UserRepository instance."""
        
        self.repository = repository
        self._logger = structlog.get_logger(__name__)

    def get_user(self, username: str) -> UserDTO:
        """Service for retrieving a user by their username."""

        try:
            self._logger.debug("user_services.get", username=username)
            user = self.repository.get_by_username(username)
            response = convert_user_model_to_user_schema_dto(user)
            self._logger.info("user_services.get.success", username=username)
            return response
        except UserNotFoundException:
            raise
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error retrieving user with username {username}: {str(e)}") from e

    def create(self, user: UserCreate) -> UserDTO:
        """Service for creating a new user in the database."""

        new_user_data = user.model_dump(exclude_unset=True)
        new_user = UserModel(**new_user_data)

        try:
            self._logger.debug("user_services.create", username=user.username)
            created_user = self.repository.create(new_user)
            response = convert_user_model_to_user_schema_dto(created_user)
            self._logger.info("user_services.create.success", username=created_user.username)
            return response
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error creating user with username {user.username}: {str(e)}") from e