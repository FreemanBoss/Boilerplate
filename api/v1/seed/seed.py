from datetime import datetime, timezone, timedelta
from sqlalchemy import text

from api.database.database import get_async_session
from api.v1.user.service import user_service
from api.v1.profile.service import (
    profile_service,
    profile_preference_service,
    profile_traits_service,
)
from api.v1.role_and_permission.service import (
    role_service,
    user_roles_service,
    permission_service,
    role_permission_service,
)
from api.v1.place.service import place_category_service, place_service
from api.v1.events.service import event_service, event_ticket_service
from api.v1.location.service import (
    location_service,
    user_location_service,
    place_location_service,
    event_location_service,
)
from api.v1.subscriptions.service import subscription_plan_service, subscription_service
from api.v1.notification.service import notification_service


async def seed_sunscription_palns(session, creator_id: str):
    """
    Seeds subscription plans.
    """
    if not await subscription_plan_service.fetch(
        {"creator_id": creator_id, "name": "free_tier", "duration": "forever"}, session
    ):
        _ = await subscription_plan_service.create(
            {"creator_id": creator_id, "name": "free_tier", "duration": "forever"},
            session,
        )
    if not await subscription_plan_service.fetch(
        {"creator_id": creator_id, "name": "weekly", "duration": "weekly"}, session
    ):
        _ = await subscription_plan_service.create(
            {"creator_id": creator_id, "name": "weekly", "duration": "weekly"}, session
        )
    if not await subscription_plan_service.fetch(
        {"creator_id": creator_id, "name": "monthly", "duration": "monthly"}, session
    ):
        _ = await subscription_plan_service.create(
            {"creator_id": creator_id, "name": "monthly", "duration": "monthly"},
            session,
        )
    if not await subscription_plan_service.fetch(
        {"creator_id": creator_id, "name": "yearly", "duration": "yearly"}, session
    ):
        _ = await subscription_plan_service.create(
            {"creator_id": creator_id, "name": "yearly", "duration": "yearly"}, session
        )


async def seed_locations(session):
    """j
    Seeds locations.
    """
    if not await location_service.fetch(
        {"city": "Abuja", "state": "Abuja", "country": "Nigeria"}, session
    ):
        await location_service.create(
            {"city": "Abuja", "state": "Abuja", "country": "Nigeria"},
            session,
        )
    if not await location_service.fetch(
        {"city": "Lagos", "state": "Lagos", "country": "Nigeria"}, session
    ):
        await location_service.create(
            {"city": "Lagos", "state": "Lagos", "country": "Nigeria"},
            session,
        )
    if not await location_service.fetch(
        {"city": "Kaduna", "state": "Kaduna", "country": "Nigeria"},
        session,
    ):
        await location_service.create(
            {"city": "Kaduna", "state": "Kaduna", "country": "Nigeria"},
            session,
        )
    if not await location_service.fetch(
        {"city": "Kano", "state": "Kano", "country": "Nigeria"}, session
    ):
        await location_service.create(
            {"city": "Kano", "state": "Kano", "country": "Nigeria"},
            session,
        )
    if not await location_service.fetch(
        {"city": "Anambra", "state": "Anambra", "country": "Nigeria"},
        session,
    ):
        await location_service.create(
            {"city": "Anambra", "state": "Anambra", "country": "Nigeria"},
            session,
        )


async def seed_permissions(session):
    """j
    Seeds permissions.
    """
    permissions = [
        {"name": "read_user", "description": "Can read user only"},
        {"name": "delete_user", "description": "Can delete user only"},
        {"name": "create_user", "description": "Can create user only"},
        {"name": "edit_user", "description": "Can edit user only"},
        {"name": "edit_self", "description": "Can edit self"},
        {"name": "delete_self", "description": "Can delete self"},
    ]

    for permission in permissions:
        if not await permission_service.fetch(permission, session):
            await permission_service.create(permission, session)


async def seed_roles(session):
    """
    Seeds roles
    """
    roles = [
        {"name": "superadmin", "description": "Super Administrator"},
        {"name": "user", "description": "Regular User."},
        {"name": "admin", "description": "Administaror."},
    ]
    for role in roles:
        if not await role_service.fetch(role, session):
            await role_service.create(role, session)


async def seed_events(session, creator_id: str):
    """
    Seeds events.
    """
    if not await event_ticket_service.fetch({"name": "VIP"}, session):
        _ = await event_ticket_service.create({"name": "VIP"}, session)
    if not await event_ticket_service.fetch({"name": "VVIP"}, session):
        _ = await event_ticket_service.create({"name": "VVIP"}, session)
    if not await event_ticket_service.fetch({"name": "personal"}, session):
        _ = await event_ticket_service.create({"name": "personal"}, session)

    if not await event_service.fetch({"name": "date VIP"}, session):
        VIP = await event_ticket_service.fetch({"name": "VIP"}, session)
        res_event = await event_service.create(
            {
                "ticket_id": VIP.id,
                "creator_id": creator_id,
                "name": "date VIP",
                "personal": {"personal_one": "some personal"},
                "about": "all good",
                "rating": 4,
                "menu_url": "some url",
            },
            session,
        )
        Abuja = await location_service.fetch(
            {"city": "Abuja", "state": "Abuja", "country": "Nigeria"}, session
        )
        if not await place_location_service.fetch(
            {"place_id": res_event.id, "location_id": Abuja.id}, session
        ):
            _ = await place_location_service.create(
                {"place_id": res_event.id, "location_id": Abuja.id}, session
            )

    if not await event_service.fetch({"name": "Lekki VIP"}, session):
        VIP = await event_ticket_service.fetch({"name": "VIP"}, session)
        VIP_event = await event_service.create(
            {
                "category_id": VIP.id,
                "creator_id": creator_id,
                "name": "Lekki VIP",
                "banner": {"VIP_one": "some VIP"},
                "about": "all good",
                "rating": 4,
                "menu_url": "some url",
            },
            session,
        )
        lagos = await location_service.fetch(
            {"city": "Lagos", "state": "Lagos", "country": "Nigeria"}, session
        )
        if not await place_location_service.fetch(
            {"place_id": VIP_event.id, "location_id": lagos.id}, session
        ):
            _ = await event_location_service.create(
                {"place_id": VIP_event.id, "location_id": lagos.id}, session
            )
    if not await event_service.fetch({"name": "Stupor Bar"}, session):
        VVIP = await event_ticket_service.fetch({"name": "Bar"}, session)
        VVIP_event = await event_service.create(
            {
                "ticket_id": VVIP.id,
                "creator_id": creator_id,
                "name": "Lekki VVIP",
                "banner": {"VVIP_one": "some VVIP"},
                "about": "all good",
                "rating": 4,
                "menu_url": "some url",
            },
            session,
        )
        kaduna = await location_service.fetch(
            {"city": "Kaduna", "state": "Kaduna", "country": "Nigeria"}, session
        )
        if not await place_location_service.fetch(
            {"place_id": VVIP_event.id, "location_id": kaduna.id}, session
        ):
            _ = await event_location_service.create(
                {"event_id": VVIP_event.id, "location_id": kaduna.id}, session
            )


async def seed_places(session, creator_id: str):
    """
    Seeds places.
    """
    if not await place_category_service.fetch({"name": "Restaurant"}, session):
        _ = await place_category_service.create({"name": "Restaurant"}, session)
    if not await place_category_service.fetch({"name": "Bar"}, session):
        _ = await place_category_service.create({"name": "Bar"}, session)
    if not await place_category_service.fetch({"name": "Hotel"}, session):
        _ = await place_category_service.create({"name": "Hotel"}, session)

    if not await place_service.fetch({"name": "food restaurant"}, session):
        restaurant = await place_category_service.fetch({"name": "Restaurant"}, session)
        res_place = await place_service.create(
            {
                "category_id": restaurant.id,
                "creator_id": creator_id,
                "name": "food restaurant",
                "banner": {"banner_one": "some banner"},
                "about": "all good",
                "rating": 4,
                "menu_url": "some url",
            },
            session,
        )
        Abuja = await location_service.fetch(
            {"city": "Abuja", "state": "Abuja", "country": "Nigeria"}, session
        )
        if not await place_location_service.fetch(
            {"place_id": res_place.id, "location_id": Abuja.id}, session
        ):
            _ = await place_location_service.create(
                {"place_id": res_place.id, "location_id": Abuja.id}, session
            )

    if not await place_service.fetch({"name": "Lekki Hotel"}, session):
        hotel = await place_category_service.fetch({"name": "Hotel"}, session)
        hotel_place = await place_service.create(
            {
                "category_id": hotel.id,
                "creator_id": creator_id,
                "name": "Lekki Bar",
                "banner": {"banner_one": "some banner"},
                "about": "all good",
                "rating": 4,
                "menu_url": "some url",
            },
            session,
        )
        lagos = await location_service.fetch(
            {"city": "Lagos", "state": "Lagos", "country": "Nigeria"}, session
        )
        if not await place_location_service.fetch(
            {"place_id": hotel_place.id, "location_id": lagos.id}, session
        ):
            _ = await place_location_service.create(
                {"place_id": hotel_place.id, "location_id": lagos.id}, session
            )
    if not await place_service.fetch({"name": "Stupor Bar"}, session):
        bar = await place_category_service.fetch({"name": "Bar"}, session)
        bar_place = await place_service.create(
            {
                "category_id": bar.id,
                "creator_id": creator_id,
                "name": "Stupor Bar",
                "banner": {"banner_one": "some banner"},
                "about": "all good",
                "rating": 4,
                "menu_url": "some url",
            },
            session,
        )
        kaduna = await location_service.fetch(
            {"city": "Kaduna", "state": "Kaduna", "country": "Nigeria"}, session
        )
        if not await place_location_service.fetch(
            {"place_id": bar_place.id, "location_id": kaduna.id}, session
        ):
            _ = await place_location_service.create(
                {"place_id": bar_place.id, "location_id": kaduna.id}, session
            )


async def seed_role_permissions(session):
    """
    Seeds role_permissions.
    """
    edit_user = await permission_service.fetch({"name": "edit_user"}, session)
    read_user = await permission_service.fetch({"name": "read_user"}, session)
    delete_user = await permission_service.fetch({"name": "delete_user"}, session)
    create_user = await permission_service.fetch({"name": "create_user"}, session)
    edit_self = await permission_service.fetch({"name": "edit_self"}, session)
    delete_self = await permission_service.fetch({"name": "delete_self"}, session)

    superadmin_role = await role_service.fetch({"name": "superadmin"}, session)
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=superadmin_role.id, permission_id=edit_user.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=superadmin_role.id, permission_id=read_user.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=superadmin_role.id, permission_id=delete_user.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=superadmin_role.id, permission_id=create_user.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=superadmin_role.id, permission_id=edit_self.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=superadmin_role.id, permission_id=delete_self.id
    )

    admin_role = await role_service.fetch({"name": "admin"}, session)
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=admin_role.id, permission_id=edit_self.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=admin_role.id, permission_id=delete_self.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=admin_role.id, permission_id=edit_user.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=admin_role.id, permission_id=read_user.id
    )

    user_role = await role_service.fetch({"name": "user"}, session)
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=user_role.id, permission_id=edit_self.id
    )
    await role_permission_service.insert_if_not_exists(
        session=session, role_id=user_role.id, permission_id=delete_self.id
    )


async def seed_users():
    """
    Seeds users to the database.
    """
    async for session in get_async_session():
        stmt = "ALTER TYPE subscription_plans_enum ADD VALUE IF NOT EXISTS 'forever';"
        await session.execute(text(stmt))
        await session.commit()

        await seed_permissions(session)
        await seed_roles(session)
        await seed_role_permissions(session)
        await seed_locations(session)

        # fetch roles
        user = await role_service.fetch({"name": "user"}, session)
        admin = await role_service.fetch({"name": "admin"}, session)
        superadmin_role = await role_service.fetch({"name": "superadmin"}, session)

        if not await user_service.fetch({"email": "firelord@gmail.com"}, session):
            firelord = await user_service.create(
                {
                    "email": "firelord@gmail.com",
                    "password": "Firelord1234#",
                    "first_name": "Firelord",
                    "last_name": "Firelord",
                    "is_deleted": False,
                    "is_suspended": False,
                    "is_active": True,
                    "email_verified": True,
                },
                session,
            )
            _ = await profile_service.create(
                {
                    "user_id": firelord.id,
                },
                session,
            )
        firelord = await user_service.fetch({"email": "firelord@gmail.com"}, session)
        await seed_places(session, firelord.id)
        await seed_sunscription_palns(session, firelord.id)

        await user_roles_service.insert_if_not_exists(
            session=session, role_id=superadmin_role.id, user_id=firelord.id
        )
        lagos = await location_service.fetch(
            {"city": "Lagos", "state": "Lagos", "country": "Nigeria"},
            session,
        )
        if not await user_location_service.fetch(
            {"user_id": firelord.id, "location_id": lagos.id}, session
        ):
            _ = await user_location_service.create(
                {"user_id": firelord.id, "location_id": lagos.id, "is_current": True},
                session,
            )

        if not await user_service.fetch({"email": "johnson@gmail.com"}, session):
            johnson = await user_service.create(
                {
                    "email": "johnson@gmail.com",
                    "password": "Johnson1234#",
                    "first_name": "Johnson",
                    "last_name": "Johnson",
                    "is_deleted": False,
                    "is_suspended": False,
                    "is_active": True,
                    "email_verified": True,
                },
                session,
            )
            johnson_profile = await profile_service.create(
                {
                    "user_id": johnson.id,
                },
                session,
            )
            _ = await profile_preference_service.create(
                {
                    "profile_id": johnson_profile.id,
                },
                session,
            )
            _ = await profile_traits_service.create(
                {
                    "profile_id": johnson_profile.id,
                },
                session,
            )
        johnson = await user_service.fetch({"email": "johnson@gmail.com"}, session)
        await user_roles_service.insert_if_not_exists(
            session=session, role_id=admin.id, user_id=johnson.id
        )
        print(johnson.id)
        anambra = await location_service.fetch(
            {"city": "Anambra", "state": "Anambra", "country": "Nigeria"},
            session,
        )
        if not await user_location_service.fetch(
            {"user_id": johnson.id, "location_id": anambra.id}, session
        ):
            _ = await user_location_service.create(
                {"user_id": johnson.id, "location_id": anambra.id, "is_current": True},
                session,
            )

        if not await user_service.fetch({"email": "jayson@gmail.com"}, session):
            jayson = await user_service.create(
                {
                    "email": "jayson@gmail.com",
                    "password": "Jayson1234#",
                    "first_name": "jayson",
                    "last_name": "jayson",
                    "is_deleted": False,
                    "is_suspended": False,
                    "is_active": True,
                    "email_verified": True,
                },
                session,
            )
            jayson_profile = await profile_service.create(
                {
                    "user_id": jayson.id,
                },
                session,
            )
            _ = await profile_preference_service.create(
                {
                    "profile_id": jayson_profile.id,
                },
                session,
            )
            _ = await profile_traits_service.create(
                {
                    "profile_id": jayson_profile.id,
                },
                session,
            )
        jayson = await user_service.fetch({"email": "jayson@gmail.com"}, session)
        await user_roles_service.insert_if_not_exists(
            session=session, role_id=user.id, user_id=jayson.id
        )
        abuja = await location_service.fetch(
            {"city": "Abuja", "state": "Abuja", "country": "Nigeria"},
            session,
        )
        if not await user_location_service.fetch(
            {"user_id": jayson.id, "location_id": abuja.id}, session
        ):
            _ = await user_location_service.create(
                {"user_id": jayson.id, "location_id": abuja.id, "is_current": True},
                session,
            )
        if not await user_service.fetch({"email": "jane@gmail.com"}, session):
            jane = await user_service.create(
                {
                    "email": "jane@gmail.com",
                    "password": "Jane1234#",
                    "first_name": "jane",
                    "last_name": "jane",
                    "is_deleted": False,
                    "is_suspended": False,
                    "is_active": True,
                    "email_verified": True,
                },
                session,
            )
            jane_profile = await profile_service.create(
                {
                    "user_id": jane.id,
                },
                session,
            )
            _ = await profile_preference_service.create(
                {
                    "profile_id": jane_profile.id,
                },
                session,
            )
            _ = await profile_traits_service.create(
                {
                    "profile_id": jane_profile.id,
                },
                session,
            )
        jane = await user_service.fetch({"email": "jane@gmail.com"}, session)
        await user_roles_service.insert_if_not_exists(
            session=session, role_id=admin.id, user_id=jane.id
        )
        kano = await location_service.fetch(
            {"city": "Kano", "state": "Kano", "country": "Nigeria"},
            session,
        )
        if not await user_location_service.fetch(
            {"user_id": jane.id, "location_id": kano.id}, session
        ):
            _ = await user_location_service.create(
                {"user_id": jane.id, "location_id": kano.id, "is_current": True},
                session,
            )
        if not await user_service.fetch({"email": "jackson@gmail.com"}, session):
            jackson = await user_service.create(
                {
                    "email": "jackson@gmail.com",
                    "password": "Jackson1234#",
                    "first_name": "jackson",
                    "last_name": "jackson",
                    "is_deleted": False,
                    "is_suspended": False,
                    "is_active": True,
                    "email_verified": True,
                },
                session,
            )
            jackson_profile = await profile_service.create(
                {
                    "user_id": jackson.id,
                },
                session,
            )
            _ = await profile_preference_service.create(
                {
                    "profile_id": jackson_profile.id,
                },
                session,
            )
            _ = await profile_traits_service.create(
                {
                    "profile_id": jackson_profile.id,
                },
                session,
            )
        jackson = await user_service.fetch({"email": "jackson@gmail.com"}, session)
        await user_roles_service.insert_if_not_exists(
            session=session, role_id=user.id, user_id=jackson.id
        )
        print(jackson.id)
        kano = await location_service.fetch(
            {"city": "Kano", "state": "Kano", "country": "Nigeria"}, session
        )
        if not await user_location_service.fetch(
            {"user_id": jackson.id, "location_id": kano.id}, session
        ):
            _ = await user_location_service.create(
                {"user_id": jackson.id, "location_id": kano.id, "is_current": True},
                session,
            )
        free_tier = await subscription_plan_service.fetch(
            {"name": "free_tier", "duration": "forever"}, session
        )
        if not await subscription_service.fetch(
            {"subscriber_id": jackson.id, "subscription_plan_id": free_tier.id}, session
        ):
            await subscription_service.create(
                {
                    "subscriber_id": jackson.id,
                    "subscription_plan_id": free_tier.id,
                    "expires_in": datetime.now(timezone.utc) + timedelta(weeks=10000),
                },
                session,
            )
        if not await user_service.fetch({"email": "judason@gmail.com"}, session):
            judason = await user_service.create(
                {
                    "email": "judason@gmail.com",
                    "password": "Judason1234#",
                    "first_name": "judason",
                    "last_name": "judason",
                    "is_deleted": False,
                    "is_suspended": False,
                    "is_active": True,
                    "email_verified": True,
                },
                session,
            )
            judason_profile = await profile_service.create(
                {
                    "user_id": judason.id,
                },
                session,
            )
            _ = await profile_preference_service.create(
                {
                    "profile_id": judason_profile.id,
                },
                session,
            )
            _ = await profile_traits_service.create(
                {
                    "profile_id": judason_profile.id,
                },
                session,
            )
        judason = await user_service.fetch({"email": "judason@gmail.com"}, session)
        await user_roles_service.insert_if_not_exists(
            session=session, role_id=user.id, user_id=judason.id
        )
        print(judason.id)
        kaduna = await location_service.fetch(
            {"city": "Kaduna", "state": "Kaduna", "country": "Nigeria"}, session
        )
        if not await user_location_service.fetch(
            {"user_id": judason.id, "location_id": kaduna.id}, session
        ):
            _ = await user_location_service.create(
                {"user_id": judason.id, "location_id": kaduna.id, "is_current": True},
                session,
            )
        weekly = await subscription_plan_service.fetch(
            {"name": "weekly", "duration": "weekly"}, session
        )
        if not await subscription_service.fetch(
            {"subscriber_id": judason.id, "subscription_plan_id": weekly.id}, session
        ):
            await subscription_service.create(
                {
                    "subscriber_id": judason.id,
                    "subscription_plan_id": weekly.id,
                    "expires_in": datetime.now(timezone.utc) + timedelta(weeks=7),
                },
                session,
            )
        if not await notification_service.fetch(
            {
                "user_id": judason.id,
                "notification_type": "message",
                "title": "welcome",
                "message": "welcomeback",
            },
            session,
        ):
            _ = await notification_service.create(
                {
                    "user_id": judason.id,
                    "notification_type": "message",
                    "title": "welcome",
                    "message": "welcomeback",
                },
                session,
            )
        if not await notification_service.fetch(
            {
                "user_id": judason.id,
                "notification_type": "message",
                "title": "Profile like",
                "message": "Jane just swiped right on your profile",
            },
            session,
        ):
            _ = await notification_service.create(
                {
                    "user_id": judason.id,
                    "notification_type": "message",
                    "title": "Profile like",
                    "message": "Jane just swiped right on your profile",
                },
                session,
            )
