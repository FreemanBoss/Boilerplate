"""added place_categories, user_locations, place_locations, places.category_id, places.about, removed places.location, places.category, locations.creator_id, locations.location

Revision ID: 6f860e8fce76
Revises: c3c2e886934c
Create Date: 2024-11-12 16:44:25.205588

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6f860e8fce76"
down_revision: Union[str, None] = "c3c2e886934c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "place_categories",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_place_categories")),
    )
    op.create_index(
        op.f("ix_place_categories_id"), "place_categories", ["id"], unique=True
    )
    op.create_table(
        "user_locations",
        sa.Column("user_id", sa.String(length=60), nullable=False),
        sa.Column("location_id", sa.String(length=60), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name=op.f("fk_user_locations_location_id_locations"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_locations_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_locations")),
    )
    op.create_index(op.f("ix_user_locations_id"), "user_locations", ["id"], unique=True)
    op.create_table(
        "place_locations",
        sa.Column("place_id", sa.String(length=60), nullable=False),
        sa.Column("location_id", sa.String(length=60), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name=op.f("fk_place_locations_location_id_locations"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["place_id"],
            ["places.id"],
            name=op.f("fk_place_locations_place_id_places"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_place_locations")),
    )
    op.create_index(
        op.f("ix_place_locations_id"), "place_locations", ["id"], unique=True
    )
    op.add_column("locations", sa.Column("city", sa.String(), nullable=True))
    op.add_column("locations", sa.Column("state", sa.String(), nullable=True))
    op.add_column("locations", sa.Column("country", sa.String(), nullable=True))
    op.add_column("locations", sa.Column("latitued", sa.Float(), nullable=True))
    op.add_column("locations", sa.Column("longitude", sa.Float(), nullable=True))
    op.drop_constraint("fk_locations_creator_id_users", "locations", type_="foreignkey")
    op.drop_column("locations", "creator_id")
    op.drop_column("locations", "location")
    op.add_column(
        "places", sa.Column("category_id", sa.String(length=60), nullable=False)
    )
    op.add_column("places", sa.Column("about", sa.String(), nullable=False))
    op.alter_column(
        "places",
        "banner",
        existing_type=sa.VARCHAR(),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        postgresql_using="banner::jsonb",
    )
    op.create_foreign_key(
        op.f("fk_places_category_id_place_categories"),
        "places",
        "place_categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_column("places", "category")
    op.drop_column("places", "location")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "places",
        sa.Column("location", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "places",
        sa.Column("category", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(
        op.f("fk_places_category_id_place_categories"), "places", type_="foreignkey"
    )
    op.alter_column(
        "places",
        "banner",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=sa.VARCHAR(),
        nullable=True,
        postgresql_using="banner::text",
    )
    op.drop_column("places", "about")
    op.drop_column("places", "category_id")
    op.add_column(
        "locations",
        sa.Column(
            "location",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "locations",
        sa.Column(
            "creator_id", sa.VARCHAR(length=60), autoincrement=False, nullable=True
        ),
    )
    op.create_foreign_key(
        "fk_locations_creator_id_users",
        "locations",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_column("locations", "longitude")
    op.drop_column("locations", "latitued")
    op.drop_column("locations", "country")
    op.drop_column("locations", "state")
    op.drop_column("locations", "city")
    op.drop_index(op.f("ix_place_locations_id"), table_name="place_locations")
    op.drop_table("place_locations")
    op.drop_index(op.f("ix_user_locations_id"), table_name="user_locations")
    op.drop_table("user_locations")
    op.drop_index(op.f("ix_place_categories_id"), table_name="place_categories")
    op.drop_table("place_categories")
    # ### end Alembic commands ###
