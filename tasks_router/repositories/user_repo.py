"""
Repository module for managing User entities in the database.

This module defines UserRepository methods for SQLAlchemy CRUD
operations on users.
"""

from sqlalchemy.orm import Session

from tasks_router.exceptions.custom_exceptions import UserNotFoundException, DatabaseOperationException
from tasks_router.models.user_model import User as UserModel

class UserRepository:
    """Repository class for managing User entities in the database."""

    def __init__(self, db_session: Session) -> None:
        """Initialize the UserRepository with a database session."""

        self.db_session = db_session

    # CRUD operation sections keep repository responsibilities grouped.

    # Read operations support current and planned service use cases.
    def get_all(self) -> list[UserModel]:
        """Retrieve all users.

        Returns:
            Persisted users from the database session.

        Raises:
            DatabaseOperationException: If the database query fails.
        """
        try:
            return self.db_session.query(UserModel).all()
        except Exception as e:
            raise DatabaseOperationException(f"Error occurred while fetching users: {str(e)}") from e

    def get_by_id(self, username: str) -> UserModel:
        """Retrieve a user by username.

        Args:
            username: Unique username used for lookup.

        Returns:
            The matching user model.

        Raises:
            UserNotFoundException: If no user exists for the username.
            DatabaseOperationException: If the database query fails.
        """
        try:
            user: UserModel | None = self.db_session.query(UserModel).filter(UserModel.username == username).first()
            if not user:
                raise UserNotFoundException(username)
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseOperationException(f"Error occurred while fetching user with username: {username}: {str(e)}") from e

    # Write operations mutate database state for user entities.
    def create(self, user: UserModel) -> UserModel:
        """Create a user record.

        Args:
            user: User model prepared for persistence.

        Returns:
            The persisted and refreshed user model.

        Raises:
            DatabaseOperationException: If persistence fails.
        """

        try:
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            return user
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error occurred while creating a new user: {str(e)}") from e

    def update(self, user: UserModel) -> UserModel:
        """Update an existing user.

        Args:
            user: User model containing latest state.

        Returns:
            The merged and refreshed user model.

        Raises:
            DatabaseOperationException: If update persistence fails.
        """
        try:
            merged_user = self.db_session.merge(user)  # Add logger here
            self.db_session.commit()
            self.db_session.refresh(merged_user)
            return merged_user
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error occurred while updating the user: {str(e)}") from e

    def delete(self, user: UserModel) -> None:
        """Delete a user.

        Args:
            user: Persisted user model to remove.

        Raises:
            DatabaseOperationException: If delete persistence fails.
        """

        try:
            self.db_session.delete(user)
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error occurred while deleting the user: {str(e)}") from e
