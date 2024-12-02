from tests.conftest_helper import create_login_payload
import pytest

from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.role_and_permission.service import role_service, permission_service
from api.v1.role_and_permission.model import user_roles


class TestRolePermissionRoute:
    """
    Test class for role permission route.
    """

    @pytest.mark.asyncio
    async def test_retrieve_roles_success(self, client, test_setup, mock_creation):
        """
        Test for successful retrieval of roles by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.get(
            url="/api/v1/roles",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 200

        data = reg_response.json()

        assert data["message"] == "Roles Retrieved Successfully."
        assert data["limit"] == 10
        assert data["page"] == 1
        assert data["total_pages"] == 1
        assert data["total_items"] == 4
        assert len(data["data"]) == 4

    @pytest.mark.asyncio
    async def test_update_roles_success(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful update of roles by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        permission = await permission_service.fetch(
            {"name": "count_cash"}, test_get_session
        )

        account_role = await role_service.fetch(
            {"name": "accountant"}, test_get_session
        )

        permissions = {
            "id": permission.id,
            "name": "count_cash",
            "description": "Can count cash only",
        }

        reg_response = client.put(
            url=f"/api/v1/roles/{account_role.id}",
            json={
                "id": f"{account_role.id}",
                "name": "accountant",
                "description": "can stil count cash",
                "permissions": [permissions],
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 201

        data = reg_response.json()

        assert data["message"] == "Roles Updated Successfully."
        assert data["data"]["description"] == "can stil count cash"

    @pytest.mark.asyncio
    async def test_create_roles_success(self, client, test_setup, mock_creation):
        """
        Test for successful create of roles by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        permissions = {
            "name": "manage_users",
            "description": "Can manage users only",
        }

        reg_response = client.post(
            url="/api/v1/roles",
            json={
                "name": "manager",
                "description": "A Manager.",
                "permissions": [permissions],
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 201

        data = reg_response.json()

        assert data["message"] == "Roles Created Successfully."
        assert data["data"]["description"] == "A Manager."

    @pytest.mark.asyncio
    async def test_create_roles_failure(self, client, test_setup, mock_creation):
        """
        Test for unsuccessful create of roles by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        permissions = {
            "name": "edit_self",
        }

        reg_response = client.post(
            url="/api/v1/roles",
            json={
                "name": "user",
                "description": "A Regular User.",
                "permissions": [permissions],
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 422

        data = reg_response.json()

        assert data["message"] == "Validation Error."

    @pytest.mark.asyncio
    async def test_create_already_existing_role(
        self, client, test_setup, mock_creation
    ):
        """
        Test for unsuccessful create of already existing roles by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        permissions = {
            "name": "edit_self",
            "description": "Can edit self only",
        }

        reg_response = client.post(
            url="/api/v1/roles",
            json={
                "name": "user",
                "description": "A Regular User.",
                "permissions": [permissions],
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 409
