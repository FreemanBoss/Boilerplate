"""4fb67e1497ee

Revision ID: ce1dc15b2c76
Revises: 6b863d13998b
Create Date: 2024-11-16 10:25:15.628205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce1dc15b2c76'
down_revision: Union[str, None] = '6b863d13998b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
