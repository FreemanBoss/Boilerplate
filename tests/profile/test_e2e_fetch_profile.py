from tests.conftest_helper import create_login_payload
import pytest


class TestFecthProfileFields:
    """
    Test class for profile retrieval route.
    """

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
        profile_id = data["data"]["profile"]["id"]

        response = client.get(
            url=f"/api/v1/profiles/{profile_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
