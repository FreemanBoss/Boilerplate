"""event to location models

Revision ID: 2e89c278f76c
Revises: 0a96c64af19d
Create Date: 2024-11-13 19:15:11.440543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e89c278f76c'
down_revision: Union[str, None] = '0a96c64af19d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_locations',
    sa.Column('event_id', sa.String(length=60), nullable=False),
    sa.Column('location_id', sa.String(length=60), nullable=False),
    sa.Column('is_current', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(length=60), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_event_locations_event_id_events'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], name=op.f('fk_event_locations_location_id_locations'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_event_locations'))
    )
    op.create_index(op.f('ix_event_locations_id'), 'event_locations', ['id'], unique=True)
    op.add_column('event_tickets', sa.Column('location_id', sa.String(length=60), nullable=False))
    op.create_foreign_key(op.f('fk_event_tickets_location_id_event_locations'), 'event_tickets', 'event_locations', ['location_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_event_tickets_location_id_event_locations'), 'event_tickets', type_='foreignkey')
    op.drop_column('event_tickets', 'location_id')
    op.drop_index(op.f('ix_event_locations_id'), table_name='event_locations')
    op.drop_table('event_locations')
    # ### end Alembic commands ###
