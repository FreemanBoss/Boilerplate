import asyncio
from typing import AsyncIterator, Union, TypeVar
from contextlib import contextmanager
from datetime import datetime
from uuid6 import uuid7
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    AsyncAttrs,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    DeclarativeBase,
    Mapped,
    mapped_column,
    declarative_mixin,
    declared_attr,
)
from sqlalchemy import (
    pool,
    create_engine,
    MetaData,
    String,
    DateTime,
    func,
)
from sqlalchemy.exc import SQLAlchemyError

from api.utils.settings import Config


if Config.TEST:
    DATABASE_URL = Config.DATABASE_URL_TEST
else:
    DATABASE_URL = Config.DATABASE_URL

# Creates the async engine, use pool_size and max_overflow for control over connections
async_engine: AsyncEngine = create_async_engine(
    url=DATABASE_URL,
    echo=False,
    future=True,
    poolclass=pool.AsyncAdaptedQueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=18000,
)

# Create a session factory, ensuring sessions are async
async_session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)

# Create scoped session tied to async loop
AsyncScoppedSession = async_scoped_session(
    session_factory=async_session_factory, scopefunc=asyncio.current_task
)


# async session
async def get_async_session() -> AsyncIterator[AsyncSession]:
    """
    Dependency to provide a database async session for each request.
    Handles session lifecycle including commit and rollback.
    """
    async with AsyncScoppedSession() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await AsyncScoppedSession.remove()
            await session.close()


# synchronous database engine
sync_engine = create_engine(
    url=Config.DATABASE_URL_SYNC,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=60,
    pool_recycle=18000,
)

# Create a session factory, ensuring sessions are sync for celery backend
sync_session_factory = sessionmaker(
    bind=sync_engine, autoflush=False, expire_on_commit=False
)

# Create scoped session tied for celery backend
SyncScoppedSession = scoped_session(
    session_factory=sync_session_factory,
)


@contextmanager
def get_sync_session():
    """
    Dependency to provide a database session for each request.
    Handles session lifecycle including commit and rollback.
    """
    session = SyncScoppedSession()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        SyncScoppedSession.remove()
        session.close()


naming_convention = {
    "ix": "ix_%(column_0_label)s",  # index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # unique
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # constraints
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # foreign key
    "pk": "pk_%(table_name)s",  # primary key
}


class Base(AsyncAttrs, DeclarativeBase):
    """
    Sqlalchemy Declarative Base.
    """

    metadata = MetaData(naming_convention=naming_convention)


T = TypeVar("T", bound="ModelMixin")


@declarative_mixin
class ModelMixin:
    """
    Mixin Class for ORM Models
    """

    id: Mapped[str] = mapped_column(
        String(60),
        default=lambda: str(uuid7()),
        primary_key=True,
        index=True,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @declared_attr
    @classmethod
    def __tablename__(cls):
        """
        Sets table name for all tables
        """
        return f"{cls.__name__.lower()}s"

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the instance"""
        obj_dict = self.__dict__.copy()
        obj_dict["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            obj_dict["updated_at"] = self.updated_at.isoformat()
        return obj_dict

    async def save(self, session: AsyncSession) -> Union[T, None]:
        """Add or update an instance in the database"""
        session.add(self)
        try:
            await session.commit()
            await session.refresh(self)
            return self
        except SQLAlchemyError as e:
            print(f"Error saving record: {e}")
            await session.rollback()
            return None
