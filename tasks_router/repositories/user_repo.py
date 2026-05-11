"""
Repository module for managing User entities in the database.
This module defines the UserRepository class, which provides methods for performing CRUD operations on User entities using SQLAlchemy ORM.
"""

from sqlalchemy.orm import Session

from tasks_router.models.user_model import User as UserModel

class UserRepository:
    """Repository class for managing User entities in the database."""

    def __init__(self, db_session: Session) -> None:
        """Initialize the UserRepository with a database session."""

        self.db_session = db_session

    # ------------------------------ CRUD operations ------------------------------

    # ------------------------------ Read operations ------------------------------

    def get_all(self) -> list[UserModel]:
        """Retrieve all users."""
        
        try:
            return self.db_session.query(UserModel).all()
        except Exception:
            raise LookupError(f"Error occurred while fetching users.")
    
    def get_by_id(self, username: str) -> UserModel | None:
        """Retrieve a user by their username."""
        
        try:
            return self.db_session.query(UserModel).filter(UserModel.username == username).first()
        except Exception:
            raise LookupError(f"Error occurred while fetching user with username: {username}")

    # ------------------------------ Write operations ------------------------------
    
    def create(self, user: UserModel) -> UserModel:
        """Create a new user in the database."""

        try:
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            return user
        except Exception:
            self.db_session.rollback()
            raise RuntimeError("Error occurred while creating a new user.")
    

    # Will not be used in the current implementation, but added for completeness and future use.
    def update(self, user: UserModel) -> UserModel:
        """Update an existing user in the database."""
        
        try:
            merged_user = self.db_session.merge(user) # Add logger here
            self.db_session.commit()
            self.db_session.refresh(merged_user)
            return merged_user
        except Exception:
            self.db_session.rollback()
            raise RuntimeError("Error occurred while updating the user.")


    # Will not be used in the current implementation, but added for completeness and future use.
    def delete(self, user: UserModel):
        """Delete a user from the database."""

        try:
            self.db_session.delete(user)
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            raise RuntimeError("Error occurred while deleting the user.")