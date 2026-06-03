"""resolve migration heads

Revision ID: d8ee742c007c
Revises: 9cd8d5f50047, e5608c27794b
Create Date: 2026-06-03 15:00:05.964216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8ee742c007c'
down_revision: Union[str, Sequence[str], None] = ('9cd8d5f50047', 'e5608c27794b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
