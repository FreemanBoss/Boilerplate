import pytest

from api.v1.reel.service import (
    reel_service,
)
from api.v1.user.service import user_service
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles


class TestReelService:
    """
    Tests class for reel service.
    """

    @pytest.mark.asyncio
    async def test_create_reel(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating reels.
        """
        async with test_get_session.begin().session as session:
            mock_jayson_user_dict.pop("confirm_password")
            # regular user jayson
            jayson_user = await user_service.create(mock_jayson_user_dict, session)
            mock_johnson_user_dict.pop("confirm_password")
            # admin user johnson
            johnson_user = await user_service.create(mock_johnson_user_dict, session)
            role = await role_service.fetch({"name": "admin"}, session)

            stmt = user_roles.insert().values(
                **{"user_id": johnson_user.id, "role_id": role.id}
            )
            await session.execute(stmt)
            await session.commit()
            await session.refresh(johnson_user)

            johnson_reel = None
            roles = [role.name for role in johnson_user.roles]
            assert "admin" in roles

            if "admin" in roles:

                johnson_reel = await reel_service.create(
                    {
                        "creator_id": johnson_user.id,
                        "url": "fakeurl",
                    },
                    session,
                )
            assert johnson_reel is not None

    @pytest.mark.asyncio
    async def test_delete_admin_sideeffect(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for delete admin does not delete the reel created by the admin.
        """
        async with test_get_session.begin().session as session:
            mock_jayson_user_dict.pop("confirm_password")

            mock_johnson_user_dict.pop("confirm_password")
            # admin user johnson
            johnson_user = await user_service.create(mock_johnson_user_dict, session)

            role = await role_service.fetch({"name": "admin"}, session)

            stmt = user_roles.insert().values(
                **{"user_id": johnson_user.id, "role_id": role.id}
            )
            await session.execute(stmt)
            await session.commit()
            await session.refresh(johnson_user)

            johnson_reel = None

            if johnson_user.roles[0].name == "admin":

                johnson_reel = await reel_service.create(
                    {
                        "creator_id": johnson_user.id,
                        "url": "fakeurl",
                    },
                    session,
                )
            assert johnson_reel is not None

            # delete admin user johnson
            _ = await user_service.delete({"id": johnson_user.id}, session)
            fetched_user = await user_service.fetch({"id": johnson_user.id}, session)
            assert fetched_user is None

            # fetch reel again
            fetched_johnson_reel = await reel_service.fetch(
                {
                    "creator_id": johnson_user.id,
                    "url": "fakeurl",
                },
                session,
            )
            assert fetched_johnson_reel is not None
