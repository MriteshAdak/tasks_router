import uuid

from .dependencies import get_user_repository

MOCK_USER_ID: uuid.UUID = get_user_repository().get_all().first().id

async def get_current_user_id() -> uuid.UUID:
    """
    Placeholder function to simulate user authentication and retrieval of the current user's ID.
    """

    return MOCK_USER_ID