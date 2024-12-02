from tests.conftest_helper import create_login_payload
from httpx import delete
import pytest

from api.v1.setting.service import setting_service


class TestProfileUpdate:
    """
    Test class for profile settings route.
    """

    @pytest.mark.asyncio
    async def test_update_user_settings(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful update
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        settings_data = {
            "language": "fr",
            "dark_mode": True,
            "voice_call": True,
            "video_call": True,
            "notifications": True,
            "anonymous_mode": True,
            "travel_mode": True,
        }

        response = client.put(
            url=f"/api/v1/profiles/settings",
            json=settings_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(response.json())

        assert response.json()["status_code"] == 200
        assert response.json()["data"]["language"] == settings_data["language"]
        assert response.json()["data"]["dark_mode"] == settings_data["dark_mode"]
        assert (
            response.json()["data"]["anonymous_mode"] == settings_data["anonymous_mode"]
        )

    @pytest.mark.asyncio
    async def test_update_non_existing_user_settings(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test update setting with users with non-existence settings
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        await setting_service.delete(
            {"user_id": johnson_superadmin.id}, test_get_session
        )

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        settings_data = {
            "language": "fr",
            "dark_mode": True,
            "voice_call": True,
            "video_call": True,
            "notifications": True,
            "anonymous_mode": True,
            "travel_mode": True,
            # "genotype": "AA",
            # "lifestyle_habits": {"ss": "ss"},
            # "lifestyle_habits": ["lifestyle_habits"],
            # "family_plans": {"family_plans": "family_plans"},
            # "religion": "tata",
            # "political_view": "political_view",
        }

        response = client.put(
            url=f"/api/v1/profiles/settings",
            json=settings_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(response.json())

        assert response.json()["status_code"] == 404

    @pytest.mark.asyncio
    async def test_update_user_settings_with_invalid_field(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for update with invalid fields
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Create test setting for the user
        _ = await setting_service.create(
            {"user_id": johnson_superadmin.id}, test_get_session
        )

        settings_data = {
            "language": "fr",
            "dark_mode": "not really",
            "voice_call": "true",
        }

        response = client.put(
            url=f"/api/v1/profiles/settings",
            json=settings_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422

    @pytest.mark.asyncio
    async def test_update_user_settings_with_unauthorized_user(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for unauthorized user
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        # Create test setting for the user
        _ = await setting_service.create(
            {"user_id": johnson_superadmin.id}, test_get_session
        )

        settings_data = {
            "language": "fr",
            "dark_mode": "yes",
        }

        response = client.put(
            url=f"/api/v1/profiles/settings",
            json=settings_data,
        )

        assert response.json()["status_code"] == 401
        assert response.json()["message"] == "Not authenticated"
