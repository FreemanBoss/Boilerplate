"""Merge heads

Revision ID: 4d09807c23c9
Revises: 3cbfd7451ec3, c3c2e886934c
Create Date: 2024-11-13 05:33:18.078382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d09807c23c9'
down_revision: Union[str, None] = ('3cbfd7451ec3', 'c3c2e886934c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
