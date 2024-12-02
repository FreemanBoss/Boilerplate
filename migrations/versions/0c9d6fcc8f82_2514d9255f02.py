"""2514d9255f02

Revision ID: 0c9d6fcc8f82
Revises: d2e5a904109a
Create Date: 2024-11-13 18:43:48.309463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c9d6fcc8f82'
down_revision: Union[str, None] = 'd2e5a904109a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
