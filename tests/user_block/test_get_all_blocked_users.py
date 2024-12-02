from tests.conftest_helper import create_login_payload
import pytest


class TestGetAllBlockedUsers:
    """
    Test class for get all blocked user route.
    """

    @pytest.mark.asyncio
    async def test_get_blocked_user_success(self, client, test_setup, mock_creation):
        """
        Test successful fetch
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # test user, user should block test user johnson_superadmin
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "User successfully blocked."
        assert response.json()["data"]["blocker_id"] == jayson_user.id
        assert response.json()["data"]["blocked_id"] == johnson_superadmin.id

        # Get all blocked users for user
        response = client.get(
            url=f"/api/v1/profiles/settings/block-lists",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "Blocked list successfully generated"
        assert response.json()["total_items"] == 1
        for data in response.json()["data"]:
            assert johnson_superadmin.id in data["blocked_id"]
            assert jayson_user.id in data["blocker_id"]

    @pytest.mark.asyncio
    async def test_get_blocked_user_with_pagination(
        self, client, test_setup, mock_creation
    ):
        """
        Test successful fetch with pagination
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # test user, user should block test user johnson_superadmin
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "User successfully blocked."
        assert response.json()["data"]["blocker_id"] == jayson_user.id
        assert response.json()["data"]["blocked_id"] == johnson_superadmin.id

        # Get all blocked users with pagination
        response = client.get(
            url=f"/api/v1/profiles/settings/block-lists?page=2&limit=5",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "Blocked list successfully generated"
        assert response.json()["total_items"] == 1
        assert response.json()["page"] == 2
        assert response.json()["limit"] == 5
        assert response.json()["data"] == []

    @pytest.mark.asyncio
    async def test_get_non_existing_blocked_user(
        self, client, test_setup, mock_creation
    ):
        """
        Test fetch for user with no blocked users
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Get all blocked users for user
        response = client.get(
            url=f"/api/v1/profiles/settings/block-lists",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "Blocked list successfully generated"
        assert response.json()["total_items"] == 0
        assert response.json()["data"] == []

    @pytest.mark.asyncio
    async def test_with_unauthorized_user(self, client, test_setup, user):
        """
        Test for delete with unauthorized user
        """

        response = client.get(
            url=f"/api/v1/profiles/settings/block-lists",
            headers={"Authorization": f"Bearer some_fake_token"},
        )

        assert response.json()["status_code"] == 401
