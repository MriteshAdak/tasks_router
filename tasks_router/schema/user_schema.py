"""
Schema definitions for user-related operations
"""

from pydantic import BaseModel, Field, AliasChoices, ConfigDict

class User(BaseModel):
    username: str = Field(validation_alias=AliasChoices('id', 'userId', 'username', 'userName', 'user_id', 'user_name'))
    display_name: str = Field(validation_alias=AliasChoices('name', 'displayName', 'display_name'))
    model_config = ConfigDict(from_attributes=True)
