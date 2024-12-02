from tests.conftest_helper import create_login_payload
import pytest


class TestProfileUpdate:
    """
    Test class for profile update route.
    """

    @pytest.mark.asyncio
    async def test_update_user_profile(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        profile_data = {
            "first_name": "Waas",
            "date_of_birth": "2024-09-04T00:00:00",
            "gender": "male",
            "joining_purpose": "date",
            "preferred_gender": "female",
            "desired_relationship": ["friendship", "long-term", "casual"],
            "height": "178.0 CM",
            "genotype": "AA",
            "hobbies": ["Football", "Writing"],
            "ideal_partner_qualities": ["Ambition", "Loyalty"],
            "lifestyle_habits": ["Drinking", "Smoking"],
            "family_plans": {"have_kids": "Kids"},
            "religion": "Male",
            "political_views": "Male",
            "bio": "I love reading...",
        }

        response = client.post(
            url=f"/api/v1/profiles",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200

    @pytest.mark.asyncio
    async def test_update_user_profile_with_incomplete_fields(
        self, client, test_setup, mock_creation
    ):
        """
        Test for update request with missing compulsory fields
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        profile_data = {
            "first_name": "Waas",
            "date_of_birth": "2024-09-04T00:00:00",
            "gender": "male",
            "joining_purpose": "date",
            "preferred_gender": "female",
        }

        response = client.post(
            url=f"/api/v1/profiles",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
