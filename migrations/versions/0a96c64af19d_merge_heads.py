"""merge heads

Revision ID: 0a96c64af19d
Revises: 0c9d6fcc8f82, 7227174020b3
Create Date: 2024-11-13 18:48:17.896478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a96c64af19d'
down_revision: Union[str, None] = ('0c9d6fcc8f82', '7227174020b3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
