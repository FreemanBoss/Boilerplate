"""Merge heads

Revision ID: d2e5a904109a
Revises: 4d09807c23c9, 6f860e8fce76
Create Date: 2024-11-13 09:46:53.560382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2e5a904109a'
down_revision: Union[str, None] = ('4d09807c23c9', '6f860e8fce76')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
