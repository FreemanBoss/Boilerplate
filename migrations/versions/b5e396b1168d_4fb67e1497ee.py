"""4fb67e1497ee

Revision ID: b5e396b1168d
Revises: ce1dc15b2c76
Create Date: 2024-11-16 10:33:51.463178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5e396b1168d'
down_revision: Union[str, None] = 'ce1dc15b2c76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
