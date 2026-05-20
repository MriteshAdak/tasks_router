import uuid

MOCK_USER_ID = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")


async def get_current_user_id() -> uuid.UUID:
    """Return a fixed user ID for local development.

    Returns:
        A deterministic UUID used until auth integration is added.
    """
    return MOCK_USER_ID
