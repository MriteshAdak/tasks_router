"""
Repository module for managing User entities in the database.
This module defines the UserRepository class, which provides methods for performing CRUD operations on User entities using SQLAlchemy ORM.
"""

import structlog
from sqlalchemy.orm import Session

from tasks_router.exceptions.custom_exceptions import UserNotFoundException, DatabaseOperationException
from tasks_router.models.user_model import User as UserModel

class UserRepository:
    """Repository class for managing User entities in the database."""

    def __init__(self, db_session: Session) -> None:
        """Initialize the UserRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session for database operations.
        """

        self.db_session = db_session
        self._logger = structlog.get_logger(__name__)

    # ------------------------------ CRUD operations ------------------------------

    # ------------------------------ Read operations ------------------------------
    
    # Will not be used in the current implementation, but added for completeness and future use.
    def get_all(self) -> list[UserModel]:
        """Retrieve all users from the database.

        Returns:
            list[UserModel]: A list of all user entities.

        Raises:
            DatabaseOperationException: When the query fails.
        """
        
        try:
            self._logger.debug("users_repo.get_all")
            return self.db_session.query(UserModel).all()
        except Exception as e:
            raise DatabaseOperationException(f"Error occurred while fetching users: {str(e)}") from e

    def get_by_username(self, username: str) -> UserModel:
        """Retrieve a user by their username.

        Args:
            username (str): Username to search for.

        Returns:
            UserModel: The user entity matching the supplied username.

        Raises:
            UserNotFoundException: When no user exists with the requested username.
            DatabaseOperationException: When the query fails.
        """
        
        try:
            self._logger.debug("users_repo.get_by_username", username=username)
            user: UserModel | None = self.db_session.query(UserModel).filter(UserModel.username == username).first()
            if not user:
                raise UserNotFoundException(username)
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseOperationException(f"Error occurred while fetching user with username: {username}: {str(e)}") from e

    # ------------------------------ Write operations ------------------------------
    
    def create(self, user: UserModel) -> UserModel:
        """Persist a new user in the database.

        Args:
            user (UserModel): The user entity to persist.

        Returns:
            UserModel: The persisted user entity.

        Raises:
            DatabaseOperationException: When the insert or commit fails.
        """

        try:
            self._logger.debug("users_repo.create", username=user.username)
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            self._logger.info("users_repo.create.success", username=user.username)
            return user
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error occurred while creating a new user: {str(e)}") from e

    # Will not be used in the current implementation, but added for completeness and future use.
    def update(self, user: UserModel) -> UserModel:
        """Update an existing user in the database."""
        
        try:
            self._logger.debug("users_repo.update", username=user.username)
            merged_user = self.db_session.merge(user) # Add logger here
            self.db_session.commit()
            self.db_session.refresh(merged_user)
            self._logger.info("users_repo.update.success", username=merged_user.username)
            return merged_user
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error occurred while updating the user: {str(e)}") from e


    # Will not be used in the current implementation, but added for completeness and future use.
    def delete(self, user: UserModel):
        """Delete a user from the database."""

        try:
            self._logger.debug("users_repo.delete", username=user.username)
            self.db_session.delete(user)
            self.db_session.commit()
            self._logger.info("users_repo.delete.success", username=user.username)
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error occurred while deleting the user: {str(e)}") from e