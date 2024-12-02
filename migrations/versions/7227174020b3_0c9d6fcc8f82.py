"""0c9d6fcc8f82

Revision ID: 7227174020b3
Revises: 2514d9255f02
Create Date: 2024-11-13 18:44:56.448158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7227174020b3'
down_revision: Union[str, None] = '2514d9255f02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
