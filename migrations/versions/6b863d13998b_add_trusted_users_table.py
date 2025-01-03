"""add trusted users table

Revision ID: 6b863d13998b
Revises: 2514d9255f02
Create Date: 2024-11-15 07:26:04.127843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6b863d13998b'
down_revision: Union[str, None] = '2514d9255f02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trusted_devices',
    sa.Column('user_id', sa.String(length=60), nullable=False),
    sa.Column('device_id', sa.String(), nullable=False),
    sa.Column('platform', sa.String(), nullable=False),
    sa.Column('device_name', sa.String(), nullable=False),
    sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_trusted', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(length=60), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_trusted_devices_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_trusted_devices'))
    )
    op.create_index(op.f('ix_trusted_devices_id'), 'trusted_devices', ['id'], unique=True)
    op.create_index(op.f('ix_trusted_devices_user_id'), 'trusted_devices', ['user_id'], unique=False)
    op.add_column('users', sa.Column('two_factor_secret', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('backup_codes', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled_at', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'two_factor_enabled_at')
    op.drop_column('users', 'backup_codes')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'two_factor_secret')
    op.drop_index(op.f('ix_trusted_devices_user_id'), table_name='trusted_devices')
    op.drop_index(op.f('ix_trusted_devices_id'), table_name='trusted_devices')
    op.drop_table('trusted_devices')
    # ### end Alembic commands ###
