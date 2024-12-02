"""empty message

Revision ID: 04e964da4e1d
Revises: 4fb67e1497ee, b5e396b1168d
Create Date: 2024-11-16 10:36:12.313051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04e964da4e1d'
down_revision: Union[str, None] = ('4fb67e1497ee', 'b5e396b1168d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
