import os
from datetime import datetime, timezone, timedelta
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import StaticPool
from datetime import datetime, timedelta, timezone

# Set TEST environment variable before importing the rest of the modules.
os.environ["TEST"] = "TEST"
from api.utils.settings import Config
from api.database.database import Base
from api.v1.role_and_permission.model import Role, Permission, role_permissions
from main import app
from api.database.database import get_async_session

from api.v1.user.service import user_service
from api.v1.profile.service import (
    profile_service,
    profile_preference_service,
    profile_traits_service,
)
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles
from api.v1.subscriptions.service import subscription_plan_service, subscription_service
from api.v1.location.service import (
    location_service,
    user_location_service,
    place_location_service,
)
from api.v1.place.service import place_service, place_category_service
from tests.notification.conftest_helper import notification_creation_helper
from tests.conftest_helper import conftest_helper
from tests.sticker.conftest_helper import create_sticker_helper

# inmemory for services
# Conditional logic for database configuration
if Config.DATABASE_URL_TEST.startswith("sqlite"):
    # SQLite-specific configuration for local testing
    test_engine = create_async_engine(
        url=Config.DATABASE_URL_TEST,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
else:
    # PostgreSQL configuration for CI (no SQLite-specific arguments)
    test_engine = create_async_engine(url=Config.DATABASE_URL_TEST)
# for services
TestSessionLocalMemory = async_sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False
)


# create database session for overriding app dependencies
@pytest.fixture(scope="function")
async def test_get_session():
    """
    Replaces get_session function for method testing.
    """
    async with TestSessionLocalMemory() as session:
        yield session
        await session.close()


async def override_get_async_session():
    """
    Overrides get_async_session generator in app instance.
    """
    async with TestSessionLocalMemory() as session:
        yield session
        await session.close()


# create database session for testing service classes
@pytest.fixture(scope="function")
async def test_setup():
    """
    create database session for testing service classes
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocalMemory() as session:
        roles = [
            {"name": "admin", "description": "Administrator"},
            {"name": "superadmin", "description": "Super Administrator"},
            {"name": "accountant", "description": "accountant"},
            {"name": "user", "description": "regular user"},
            {
                "name": "content_creator",
                "description": "A content creator",
            },
        ]

        permissions = [
            {"name": "read_user", "description": "Can read user only"},
            {"name": "delete_user", "description": "Can delete user only"},
            {"name": "create_user", "description": "Can create user only"},
            {"name": "edit_user", "description": "Can edit user only"},
            {"name": "count_cash", "description": "Can count cash only"},
            {"name": "edit_self", "description": "Can edit self"},
        ]

        role_admin = Role(**roles[0])
        role_superadmin = Role(**roles[1])
        role_accountant = Role(**roles[2])
        role_user = Role(**roles[3])

        permissions_read_user = Permission(**permissions[0])
        permissions_delete_user = Permission(**permissions[1])
        permissions_create_user = Permission(**permissions[2])
        permissions_edit_user = Permission(**permissions[3])
        permissions_count_cash = Permission(**permissions[4])
        permissions_edit_self = Permission(**permissions[5])

        role_user.permissions.append(permissions_edit_self)
        role_accountant.permissions.append(permissions_count_cash)
        role_admin.permissions.append(permissions_read_user)
        role_admin.permissions.append(permissions_edit_user)
        role_superadmin.permissions.append(
            permissions_read_user,
        )
        role_superadmin.permissions.append(
            permissions_edit_user,
        )
        role_superadmin.permissions.append(
            permissions_create_user,
        )
        role_superadmin.permissions.append(
            permissions_delete_user,
        )

        session = TestSessionLocalMemory()
        session.add_all(
            [
                permissions_edit_self,
                role_admin,
                role_superadmin,
                role_accountant,
                permissions_create_user,
                permissions_delete_user,
                permissions_edit_user,
                permissions_read_user,
                permissions_count_cash,
                role_user,
            ]
        )

        await session.commit()

        superadmin_user = await user_service.create(
            {"password": "Johnson1234#", "email": "superadmin@gmail.com"}, session
        )

        _ = await subscription_plan_service.create(
            {
                "creator_id": superadmin_user.id,
                "name": "free_tier",
                "duration": "forever",
            },
            session,
        )

        _ = await subscription_plan_service.create(
            {"creator_id": superadmin_user.id, "name": "weekly", "duration": "weekly"},
            session,
        )
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def client():
    """
    Replaces the instance of the main app
    """
    client = TestClient(app)
    yield client


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="function")
def mock_johnson_user_dict():
    """
    Mock dict input for johnson user
    """
    register_input = {
        "email": "johnson@gmail.com",
        "first_name": "johnson",
        "last_name": "oragui",
        "password": "Johnson1234@",
        "confirm_password": "Johnson1234@",
        "idempotency_key": "johnson_idempotency-key",
        "is_deleted": False,
        "is_suspended": False,
    }
    yield register_input


@pytest.fixture(scope="function")
def mock_jayson_user_dict():
    """
    Mock dict input for jayson
    """
    register_input = {
        "email": "jayson@gmail.com",
        "first_name": "jayson",
        "last_name": "oragui",
        "password": "Jayson1234@",
        "confirm_password": "Jayson1234@",
        "idempotency_key": "fake_idempotency-key",
        "is_deleted": False,
        "is_suspended": False,
    }
    yield register_input


@pytest.fixture(scope="function")
def mock_subcsription_plan_dict():
    """
    Mock dict input for subscription plan
    """
    subscription_plan_input = {
        "creator_id": "",
        "name": "weekly plan",
        "duration": "weekly",
        "amount": 5.0,
        "price": 5.0,
        "banner_url": "fake_url",
    }
    yield subscription_plan_input


@pytest.fixture(scope="function")
def mock_subcsription_plan_dict_two():
    """
    Mock dict input for subscription plan
    """
    subscription_plan_input = {
        "creator_id": "",
        "name": "weekly plan",
        "duration": "monthly",
        "amount": 5.0,
        "price": 5.0,
        "banner_url": "fake_url",
    }
    yield subscription_plan_input


@pytest.fixture(scope="function")
def mock_subcsription_dict():
    """
    Mock dict input for subscription
    """
    subscription_input = {
        "subscriber_id": "",
        "subscription_plan_id": "",
        "expires_in": datetime.now(timezone.utc) + timedelta(days=7),
        "status": "active",
    }
    yield subscription_input


@pytest.fixture(scope="function")
def mock_subcsription_dict_two():
    """
    Mock dict input for subscription
    """
    subscription_input = {
        "subscriber_id": "",
        "subscription_plan_id": "",
        "expires_in": datetime.now(timezone.utc) + timedelta(days=7),
        "status": "active",
    }
    yield subscription_input


# Restore environment variable after tests
@pytest.fixture(scope="session", autouse=True)
def restore_test_env():
    """
    Restore environment variable after tests
    """
    yield
    os.environ["TEST"] = ""


@pytest.fixture(scope="function")
async def user(test_get_session, mock_johnson_user_dict):
    mock_johnson_user_dict["secret_token_identifier"] = "test_secret"
    mock_johnson_user_dict.pop("confirm_password")
    mock_johnson_user_dict["email_verified"] = True

    user = await user_service.create(mock_johnson_user_dict, test_get_session)
    profile = await profile_service.create({"user_id": user.id}, test_get_session)
    profile_traits = await profile_traits_service.create(
        {"profile_id": profile.id}, test_get_session
    )
    profile_preference = await profile_preference_service.create(
        {"profile_id": profile.id}, test_get_session
    )
    free_tier = await subscription_plan_service.fetch(
        {
            "name": "free_tier",
            "duration": "forever",
        },
        test_get_session,
    )
    johnson_sub = await subscription_service.create(
        {
            "subscriber_id": user.id,
            "subscription_plan_id": free_tier.id,
            "expires_in": datetime.now(timezone.utc) + timedelta(weeks=7),
        },
        test_get_session,
    )

    role = await role_service.fetch({"name": "user"}, test_get_session)

    stmt = user_roles.insert().values(**{"user_id": user.id, "role_id": role.id})
    await test_get_session.execute(stmt)
    await test_get_session.commit()
    return user


@pytest.fixture(scope="function")
async def superadmin(test_get_session, mock_jayson_user_dict):
    mock_jayson_user_dict["secret_token_identifier"] = "test_secret"
    mock_jayson_user_dict.pop("confirm_password")
    mock_jayson_user_dict["email_verified"] = True

    superadmin_user = await user_service.create(mock_jayson_user_dict, test_get_session)
    profile = await profile_service.create(
        {"user_id": superadmin_user.id}, test_get_session
    )

    role = await role_service.fetch({"name": "superadmin"}, test_get_session)
    free_tier = await subscription_plan_service.fetch(
        {
            "name": "free_tier",
            "duration": "forever",
        },
        test_get_session,
    )
    johnson_sub = await subscription_service.create(
        {
            "subscriber_id": superadmin_user.id,
            "subscription_plan_id": free_tier.id,
            "expires_in": datetime.now(timezone.utc) + timedelta(weeks=7),
        },
        test_get_session,
    )

    stmt = user_roles.insert().values(
        **{"user_id": superadmin_user.id, "role_id": role.id}
    )
    await test_get_session.execute(stmt)
    await test_get_session.commit()
    return superadmin_user


@pytest.fixture(scope="function")
async def place_location_subscription(
    test_get_session, mock_johnson_user_dict, mock_jayson_user_dict
):
    mock_johnson_user_dict["secret_token_identifier"] = "test_secret"
    mock_johnson_user_dict.pop("confirm_password")
    mock_johnson_user_dict["email_verified"] = True

    superadmin_user = await user_service.create(
        mock_johnson_user_dict, test_get_session
    )
    _ = await profile_service.create({"user_id": superadmin_user.id}, test_get_session)

    role = await role_service.fetch({"name": "superadmin"}, test_get_session)

    stmt = user_roles.insert().values(
        **{"user_id": superadmin_user.id, "role_id": role.id}
    )
    await test_get_session.execute(stmt)
    await test_get_session.commit()

    mock_jayson_user_dict.pop("confirm_password")
    mock_jayson_user_dict["email_verified"] = True

    jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
    _ = await profile_service.create({"user_id": jayson_user.id}, test_get_session)

    role = await role_service.fetch({"name": "user"}, test_get_session)

    stmt = user_roles.insert().values(**{"user_id": jayson_user.id, "role_id": role.id})
    await test_get_session.execute(stmt)
    await test_get_session.commit()

    # week
    free_tier = await subscription_plan_service.fetch(
        {
            "name": "free_tier",
            "duration": "forever",
        },
        test_get_session,
    )

    weekly = await subscription_plan_service.fetch(
        {"name": "weekly", "duration": "weekly"},
        test_get_session,
    )

    abuja = await location_service.create(
        {"city": "Abuja", "state": "Abuja", "country": "Nigeria"},
        test_get_session,
    )

    lagos = await location_service.create(
        {"city": "Lagos", "state": "Lagos", "country": "Nigeria"},
        test_get_session,
    )

    jayson_sub = await subscription_service.create(
        {
            "subscriber_id": jayson_user.id,
            "subscription_plan_id": free_tier.id,
            "expires_in": datetime.now(timezone.utc) + timedelta(weeks=1000),
        },
        test_get_session,
    )
    johnson_sub = await subscription_service.create(
        {
            "subscriber_id": superadmin_user.id,
            "subscription_plan_id": weekly.id,
            "expires_in": datetime.now(timezone.utc) + timedelta(weeks=7),
        },
        test_get_session,
    )

    johnson_location = await user_location_service.create(
        {"user_id": superadmin_user.id, "location_id": lagos.id, "is_current": True},
        test_get_session,
    )
    jayson_location = await user_location_service.create(
        {"user_id": jayson_user.id, "location_id": abuja.id, "is_current": True},
        test_get_session,
    )

    restaurant = await place_category_service.create(
        {"name": "Restaurant"}, test_get_session
    )

    hotel = await place_category_service.create({"name": "Hotel"}, test_get_session)

    res_place = await place_service.create(
        {
            "category_id": restaurant.id,
            "creator_id": johnson_location.id,
            "name": "food restaurant",
            "banner": {"banner_one": "some banner"},
            "about": "all good",
            "rating": 4,
            "menu_url": "some url",
        },
        test_get_session,
    )

    hotel_place = await place_service.create(
        {
            "category_id": hotel.id,
            "creator_id": johnson_location.id,
            "name": "Hotel Lekki",
            "banner": {"banner_one": "some banner"},
            "about": "all good",
            "rating": 4,
            "menu_url": "some url",
        },
        test_get_session,
    )

    res_place_location = await place_location_service.create(
        {"place_id": res_place.id, "location_id": abuja.id}, test_get_session
    )
    hotel_place_location = await place_location_service.create(
        {"place_id": hotel_place.id, "location_id": lagos.id}, test_get_session
    )

    yield res_place, hotel_place


@pytest.fixture(scope="function")
async def mock_notification_creation(test_get_session, mock_jayson_user_dict):
    jayson, notifications = await notification_creation_helper(
        test_get_session, mock_jayson_user_dict
    )
    yield jayson, notifications


@pytest.fixture(scope="function")
async def mock_creation(
    test_get_session, mock_jayson_user_dict, mock_johnson_user_dict
):
    johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = (
        await conftest_helper(
            test_get_session, mock_jayson_user_dict, mock_johnson_user_dict
        )
    )
    yield johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly
