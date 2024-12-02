from tests.conftest_helper import create_login_payload
import pytest

from api.v1.setting.service import setting_service


class TestDeleteUser:
    """
    Test class for profile settings route.
    """

    @pytest.mark.asyncio
    async def test_delete_user_success(self, client, test_setup, superadmin):
        """
        Test for successful delete
        """
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.delete(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "User successfully deleted"

    @pytest.mark.asyncio
    async def test_delete_unauthorized_user(self, client, test_setup, mock_creation):
        """
        Test for delete with unauthorized user
        """

        response = client.delete(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer some_fake_token"},
        )

        assert response.json()["status_code"] == 401

    @pytest.mark.asyncio
    async def test_delete_user_twice(self, client, test_setup, mock_creation):
        """
        Test for attempt to delete a user twice
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # First attempt
        response = client.delete(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200

        # Second attempt
        response = client.delete(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 403
        assert response.json()["message"] == "User is no longer a part of the platform."
