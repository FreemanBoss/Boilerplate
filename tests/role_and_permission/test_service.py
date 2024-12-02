import pytest

from api.v1.role_and_permission.model import (
    Role,
    Permission,
    role_permissions,
    user_roles,
)
from api.v1.user.service import user_service
from api.v1.role_and_permission.service import role_service


class TestRoleAndPermission:
    """
    Test class for role and permission
    """

    @pytest.mark.asyncio
    async def test_create_roles_and_permissions(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        tests successfull creation of roles and permissions, and role_permissions
        """
        async with test_get_session.begin().session as session:
            roles = [
                {"name": "dancer", "description": "Administrator"},
                {"name": "seer", "description": "Super Administrator"},
                {"name": "baller", "description": "accountant"},
                {"name": "mega", "description": "regular user"},
                {
                    "name": "content_creator",
                    "description": "A content creator",
                },
            ]

            permissions = [
                {"name": "read_random", "description": "Can read random only"},
                {"name": "delete_random", "description": "Can delete random only"},
                {"name": "create_random", "description": "Can create random only"},
                {"name": "edit_random", "description": "Can edit random only"},
            ]

            role_admin = Role(**roles[0])
            role_superadmin = Role(**roles[1])
            role_accountant = Role(**roles[2])
            role_user = Role(**roles[3])

            permissions_read_user = Permission(**permissions[0])
            permissions_delete_user = Permission(**permissions[1])
            permissions_create_user = Permission(**permissions[2])
            permissions_edit_user = Permission(**permissions[3])

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

            session.add_all(
                [
                    role_admin,
                    role_superadmin,
                    role_accountant,
                    role_user,
                    permissions_create_user,
                    permissions_delete_user,
                    permissions_edit_user,
                    permissions_read_user,
                ]
            )

            await session.commit()
        stmt = role_permissions.select()
        result = await test_get_session.execute(stmt)

        all_role_permissions = result.scalars().all()
        # should be 14 including the already existing role_permissons
        assert len(all_role_permissions) == 14

    @pytest.mark.asyncio
    async def test_deassociate_role_and_user(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        test_deassociate_role_and_user
        """
        async with test_get_session.begin().session as session:
            mock_johnson_user_dict.pop("confirm_password")
            mock_johnson_user_dict["email_verified"] = True

            johnson_user = await user_service.create(
                mock_johnson_user_dict, test_get_session
            )

            role = await role_service.fetch({"name": "user"}, session)

            stmt = (
                user_roles.insert()
                .values(**{"user_id": johnson_user.id, "role_id": role.id})
                .returning(user_roles)
            )
            result = await session.execute(stmt)
            user_role = result.scalar_one_or_none()
            await session.commit()

            assert johnson_user is not None
            stmt = user_roles.delete().where(
                user_roles.c.user_id == johnson_user.id, user_roles.c.role_id == role.id
            )

            await session.execute(stmt)
            await session.commit()

            stmt = user_roles.select().where(user_roles.c.user_id == johnson_user.id)

            result = await session.execute(stmt)
            await session.commit()

            user_role = result.scalar_one_or_none()

            assert user_role is None
