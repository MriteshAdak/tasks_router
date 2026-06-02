"""Another Initialization of the same schema

Revision ID: 751951f0ac39
Revises: 899ad83bc79f
Create Date: 2026-06-03 00:10:15.661500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '751951f0ac39'
down_revision: Union[str, Sequence[str], None] = '899ad83bc79f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
