from datetime import datetime, timezone, timedelta

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
)
from api.v1.setting.service import setting_service


async def conftest_helper(
    test_get_session, mock_jayson_user_dict, mock_johnson_user_dict
):
    mock_johnson_user_dict["secret_token_identifier"] = "test_secret"
    mock_johnson_user_dict.pop("confirm_password")
    mock_johnson_user_dict["email_verified"] = True

    johnson_superadmin = await user_service.create(
        mock_johnson_user_dict, test_get_session
    )
    johnson_profile = await profile_service.create(
        {"user_id": johnson_superadmin.id}, test_get_session
    )
    _ = await profile_preference_service.create(
        {"profile_id": johnson_profile.id}, test_get_session
    )
    _ = await profile_traits_service.create(
        {"profile_id": johnson_profile.id}, test_get_session
    )

    role = await role_service.fetch({"name": "superadmin"}, test_get_session)

    stmt = user_roles.insert().values(
        **{"user_id": johnson_superadmin.id, "role_id": role.id}
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
            "subscriber_id": johnson_superadmin.id,
            "subscription_plan_id": weekly.id,
            "expires_in": datetime.now(timezone.utc) + timedelta(weeks=7),
        },
        test_get_session,
    )

    johnson_location = await user_location_service.create(
        {"user_id": johnson_superadmin.id, "location_id": lagos.id, "is_current": True},
        test_get_session,
    )
    jayson_location = await user_location_service.create(
        {"user_id": jayson_user.id, "location_id": abuja.id, "is_current": True},
        test_get_session,
    )
    _ = await setting_service.create(
        {"user_id": johnson_superadmin.id}, test_get_session
    )
    _ = await setting_service.create({"user_id": jayson_user.id}, test_get_session)

    return johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly

def create_login_payload(email: str, password: str):
    return {
        "email": email,
        "password": password,
        "device_info": {
            "device_id": "akjfokallkd09u0454l5lkaj095",
            "platform": "ios",
            "device_name": "Galaxy S8",
            "app_version": "1.0.0",
        }
    }

