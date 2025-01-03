"""added roles, permissions, user_roles, and role_permissions tables

Revision ID: ecee9b465ac8
Revises: 7642f6c45f81
Create Date: 2024-11-06 07:49:03.559470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecee9b465ac8'
down_revision: Union[str, None] = '7642f6c45f81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('permissions',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('id', sa.String(length=60), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_permissions')),
    sa.UniqueConstraint('name', name=op.f('uq_permissions_name'))
    )
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=True)
    op.create_table('roles',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('id', sa.String(length=60), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles')),
    sa.UniqueConstraint('name', name=op.f('uq_roles_name'))
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=True)
    op.create_table('role_permissions',
    sa.Column('role_id', sa.String(), nullable=False),
    sa.Column('permission_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], name=op.f('fk_role_permissions_permission_id_permissions'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_role_permissions_role_id_roles'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('role_id', 'permission_id', name=op.f('pk_role_permissions'))
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('role_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_user_roles_role_id_roles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_roles_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id', name=op.f('pk_user_roles'))
    )
    op.add_column('notifications', sa.Column('title', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notifications', 'title')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_permissions_id'), table_name='permissions')
    op.drop_table('permissions')
    # ### end Alembic commands ###
