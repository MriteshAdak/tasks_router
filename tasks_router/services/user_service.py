"""
UserService class that provides business logic for user management operations.
This module defines the UserService class, which interacts with the UserRepository to perform CRUD operations on User entities. The UserService class also handles the conversion of UserModel instances to UserSchemas for API responses.
"""

from tasks_router.schema.user_schema import User as UserSchema
from tasks_router.models.user_model import User as UserModel
from tasks_router.repositories.user_repo import UserRepository
from tasks_router.utils import convert_user_model_to_user_dto_schema

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        """Initialize the UserService with a UserRepository instance."""
        
        self.repository = repository

    def get_user(self, username: str) -> UserSchema | None:
        """Service for retrieving a user by their username."""

        user = self.repository.get_by_id(username)
        return convert_user_model_to_user_dto_schema(user) if user else None
    
    def create(self, user: UserSchema) -> UserSchema:
        """Service for creating a new user in the database."""

        new_user = UserModel(
            username=user.username,
            display_name=user.display_name,
        )
        created_user = self.repository.create(new_user)
        return convert_user_model_to_user_dto_schema(created_user)