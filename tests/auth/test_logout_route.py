# tests/auth/test_logout_route.py
import pytest

from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles
from tests.conftest_helper import create_login_payload


class TestLogoutRoute:
    """
    Test class for logout route.
    """

    @pytest.mark.asyncio
    async def test_logout_success(self, client, test_setup, mock_creation):
        """
        Test for successful logout with valid access token.
        """

        # Login to get access token
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@")
        )
        assert login_response.status_code == 200
        data = login_response.json()
        access_token = data["data"]["access_token"]
        refresh_token = data["data"]["refresh_token"]

        # Test logout
        client.cookies.set("refresh_token", refresh_token)
        logout_response = client.post(
            url="/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert logout_response.status_code == 200
        data = logout_response.json()
        assert data["message"] == "Logout successful"
        client.cookies.delete("refresh_token")

    @pytest.mark.asyncio
    async def test_logout_no_token(self, client):
        """
        Test for unsuccessful logout without access token.
        """
        logout_response = client.post(
            url="/api/v1/auth/logout", headers={"Authorization": "Bearer"}
        )

        assert logout_response.status_code == 401
        data = logout_response.json()
        assert data["message"] == "Authentication required to log out"

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, client):
        """
        Test for unsuccessful logout with an invalid token.
        """
        logout_response = client.post(
            url="/api/v1/auth/logout", headers={"Authorization": "Bearer invalid_token"}
        )

        assert logout_response.status_code == 401
        data = logout_response.json()
        assert data["message"] == "Authentication required to log out"

    @pytest.mark.asyncio
    async def test_logout_expired_token(self, client):
        """
        Test for unsuccessful logout with an expired token.
        """
        logout_response = client.post(
            url="/api/v1/auth/logout",
            headers={"Authorization": f"Bearer expired_token"},
        )

        assert logout_response.status_code == 401
        data = logout_response.json()
        assert data["message"] == "Authentication required to log out"
