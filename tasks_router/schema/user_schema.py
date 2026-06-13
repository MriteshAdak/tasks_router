"""
Schema definitions for user-related operations
"""

import uuid

from pydantic import BaseModel, Field, AliasChoices, ConfigDict

class User(BaseModel):
    """Response schema for a user object.

    Attributes:
        id (uuid.UUID): Unique identifier for the user.
        username (str): Username of the user.
        display_name (str): Display name of the user.
    """

    id: uuid.UUID

    username: str = Field(
        validation_alias=AliasChoices(
            'username',
            'userId',
            'userName',
            'user_id',
            'user_name'
        )
    )
    
    display_name: str = Field(
        validation_alias=AliasChoices(
            'display_name',
            'displayName',
            'name'
        )
    )
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """Request schema for creating a new user.

    Attributes:
        username (str): Username of the new user.
        display_name (str): Display name of the new user.
    """
    
    username: str = Field(
        validation_alias=AliasChoices(
            'username',
            'userId',
            'userName',
            'user_id',
            'user_name'
        )
    )
    
    display_name: str = Field(
        validation_alias=AliasChoices(
            'display_name',
            'displayName',
            'name'
        )
    )
    
    model_config = ConfigDict(from_attributes=True)
