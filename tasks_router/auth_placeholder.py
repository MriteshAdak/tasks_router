import uuid

from .dependencies import get_user_repository

MOCK_USER_ID: uuid.UUID

async def get_current_user_id() -> uuid.UUID:
    """
    Placeholder function to simulate user authentication and retrieval of the current user's ID.
    """
    global MOCK_USER_ID
    MOCK_USER_ID = get_user_repository().get_all().first().id

    return MOCK_USER_ID