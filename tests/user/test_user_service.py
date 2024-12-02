import pytest

from api.v1.user.service import user_service
from api.v1 import enum_types
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles


class TestUserService:
    """
    Tests class for user service.
    """

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating users.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_johnson_user_dict.pop("confirm_password")
        # admin user johnson
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        role = await role_service.fetch({"name": "user"}, test_get_session)

        stmt = user_roles.insert().values(
            **{"user_id": jayson_user.id, "role_id": role.id}
        )
        await test_get_session.execute(stmt)
        await test_get_session.commit()
        await test_get_session.refresh(jayson_user)

        assert johnson_user is not None
        assert jayson_user is not None
        roles = [role.name for role in jayson_user.roles]
        assert "user" in roles

    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for delete users.
        """
        async with test_get_session.begin().session as session:
            mock_jayson_user_dict.pop("confirm_password")
            # regular user jayson
            jayson_user = await user_service.create(mock_jayson_user_dict, session)
            mock_johnson_user_dict.pop("confirm_password")
            # admin user johnson
            johnson_user = await user_service.create(mock_johnson_user_dict, session)

            role = await role_service.fetch({"name": "user"}, session)

            stmt = user_roles.insert().values(
                **{"user_id": jayson_user.id, "role_id": role.id}
            )
            await session.execute(stmt)
            await session.commit()
            await session.refresh(jayson_user)

            assert johnson_user is not None
            assert jayson_user is not None
            roles = [role.name for role in jayson_user.roles]
            assert "user" in roles

            _ = await user_service.delete({"id": jayson_user.id}, session)

            fetched_jayson = await user_service.delete({"id": jayson_user.id}, session)

            assert fetched_jayson is False
