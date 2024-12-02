from logging.config import fileConfig
from decouple import config as decouple_config
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from api.v1.activity_log.model import ActivityLog
from api.v1.comment.model import (
    ReelComment,
    PhotoComment,
    ProductComment,
)
from api.v1.date_invitation.model import DateInvitation
from api.v1.dyt_token.model import DytToken
from api.v1.events.model import Event, EventTicket
from api.v1.gift.model import Gift, ExchangedGift
from api.v1.like.model import (
    PhotoCommentLike,
    ProductLike,
    PhotoLike,
    ProductCommentLike,
    ReelCommentLike,
    ReelLike,
)
from api.v1.library.model import Library
from api.v1.auth.model import PasswordResetToken
from api.v1.location.model import Location
from api.v1.match.model import Match
from api.v1.payments.model import Payment
from api.v1.product.model import Product
from api.v1.photo.model import Photo
from api.v1.profile.model import Profile, ProfilePreference, ProfileTrait
from api.v1.reel.model import Reel
from api.v1.setting.model import Setting
from api.v1.sticker.model import Sticker, ExchangedSticker
from api.v1.subscriptions.model import Subscription, SubscriptionPlan
from api.v1.user.model import User
from api.v1.user_device.model import UserDevice
from api.v1.user_exit_feedback.model import UserExitFeedback
from api.v1.verification_request.model import VerificationRequest
from api.v1.wallet.model import Wallet
from api.v1.withdrawal.model import Withdrawal
from api.v1.role_and_permission.model import (
    Role,
    Permission,
    user_roles,
    role_permissions,
)
from api.database.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = decouple_config("DATABASE_URL_SYNC")

config.set_main_option("sqlalchemy.url", database_url)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
