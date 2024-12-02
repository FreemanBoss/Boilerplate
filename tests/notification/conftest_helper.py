from datetime import datetime, timezone, timedelta

from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles
from api.v1.subscriptions.service import subscription_plan_service, subscription_service
from api.v1.location.service import (
    location_service,
    user_location_service,
)
from api.v1.notification.service import notification_service


async def notification_creation_helper(test_get_session, mock_jayson_user_dict):

    mock_jayson_user_dict.pop("confirm_password")
    mock_jayson_user_dict["email_verified"] = True

    jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
    _ = await profile_service.create({"user_id": jayson_user.id}, test_get_session)

    role = await role_service.fetch({"name": "user"}, test_get_session)

    stmt = user_roles.insert().values(**{"user_id": jayson_user.id, "role_id": role.id})
    await test_get_session.execute(stmt)
    await test_get_session.commit()

    # week
    free_tier = await subscription_plan_service.create(
        {
            "creator_id": jayson_user.id,
            "name": "free_tier",
            "duration": "forever",
        },
        test_get_session,
    )

    abuja = await location_service.create(
        {"city": "Abuja", "state": "Abuja", "country": "Nigeria"},
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

    jayson_location = await user_location_service.create(
        {"user_id": jayson_user.id, "location_id": abuja.id, "is_current": True},
        test_get_session,
    )

    notifications = await notification_service.create_all(
        [
            {
                "message": "insentives are out!",
                "title": "insentives",
                "user_id": jayson_user.id,
                "notification_type": "alert",
            },
            {
                "message": "welcome back son!",
                "title": "welcome back",
                "user_id": jayson_user.id,
                "notification_type": "message",
            },
        ],
        test_get_session,
    )

    return jayson_user, notifications
