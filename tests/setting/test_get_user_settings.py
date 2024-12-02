from tests.conftest_helper import create_login_payload
import pytest

from api.v1.setting.service import setting_service


class TestProfileUpdate:
    """
    Test class for profile settings route.
    """

    @pytest.mark.asyncio
    async def test_get_user_settings(
        self, client, test_setup, mock_creation, test_get_session
    ):
        """
        Test for successful update
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "Settings successfully fetched."
        assert response.json()["data"]["user_id"] == jayson_user.id
        assert response.json()["data"]["anonymous_mode"] == False

    @pytest.mark.asyncio
    async def test_get_non_existing_user_settings(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test get non-existenting user settings
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        # Create test setting for the user
        _ = await setting_service.delete({"user_id": jayson_user.id}, test_get_session)

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404
        assert response.json()["message"] == "Settings not found"

    @pytest.mark.asyncio
    async def test_get_user_settings_with_unauthorized_user(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for unauthorized user
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        # Create test setting for the user
        _ = await setting_service.create({"user_id": jayson_user.id}, test_get_session)

        response = client.get(url=f"/api/v1/profiles/settings")

        assert response.json()["status_code"] == 401
        assert response.json()["message"] == "Not authenticated"
