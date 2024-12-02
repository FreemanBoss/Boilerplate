"""add profile photos table

Revision ID: c3c2e886934c
Revises: f15bcac6097f
Create Date: 2024-11-12 13:40:14.866378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3c2e886934c'
down_revision: Union[str, None] = 'f15bcac6097f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profile_photos',
    sa.Column('user_id', sa.String(length=60), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(length=60), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_profile_photos_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_profile_photos'))
    )
    op.create_index(op.f('ix_profile_photos_id'), 'profile_photos', ['id'], unique=True)
    op.create_index(op.f('ix_profile_photos_user_id'), 'profile_photos', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_profile_photos_user_id'), table_name='profile_photos')
    op.drop_index(op.f('ix_profile_photos_id'), table_name='profile_photos')
    op.drop_table('profile_photos')
    # ### end Alembic commands ###
