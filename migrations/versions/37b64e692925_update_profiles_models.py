"""update profiles models

Revision ID: 37b64e692925
Revises: 986d74c6bb2b
Create Date: 2024-11-10 22:44:07.995614

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "37b64e692925"
down_revision: Union[str, None] = "986d74c6bb2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "profile_preferences",
        "desired_relationship",
        existing_type=sa.VARCHAR(length=100),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=True,
        postgresql_using="desired_relationship::jsonb",
    )  # Adding USING clause
    op.alter_column(
        "profiles",
        "height",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.String(),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "profiles",
        "height",
        existing_type=sa.String(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=True,
        postgresql_using="height::double precision",
    )
    op.alter_column(
        "profile_preferences",
        "desired_relationship",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=sa.VARCHAR(length=100),
        existing_nullable=True,
        postgresql_using="desired_relationship::text",
    )  # Add USING for downgrade if needed
    # ### end Alembic commands ###
