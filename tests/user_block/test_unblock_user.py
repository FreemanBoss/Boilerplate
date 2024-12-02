from tests.conftest_helper import create_login_payload
import pytest


class TestUnblockUser:
    """
    Test class for user unblock route.
    """

    @pytest.mark.asyncio
    async def test_unblock_user_success(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful unblock
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # user blocks test superadmin
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "User successfully blocked."
        assert response.json()["data"]["blocker_id"] == jayson_user.id
        assert response.json()["data"]["blocked_id"] == johnson_superadmin.id

        # user unblocks superadmin
        response = client.delete(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "User successfully unblocked"

    @pytest.mark.asyncio
    async def test_unblock_yourself(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test unblocking oneself
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # test user unblocking user
        response = client.delete(
            url=f"/api/v1/profiles/settings/block-lists/{jayson_user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 400
        assert response.json()["message"] == "Cannot unblock yourself"

    @pytest.mark.asyncio
    async def test_unblock_non_existing_user(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test blocking non-existing user
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # test unblocking non existing user is
        response = client.delete(
            url=f"/api/v1/profiles/settings/block-lists/{"some_fake_id"}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 404
        assert (
            response.json()["message"]
            == "Block record not found or user is not blocked"
        )

    @pytest.mark.asyncio
    async def test_unblock_non_blocked_user(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test unblocking a user that's not blocked
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # test unblocking a user that's not blocked
        response = client.delete(
            url=f"/api/v1/profiles/settings/block-lists/{jayson_user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 404
        assert (
            response.json()["message"]
            == "Block record not found or user is not blocked"
        )

    @pytest.mark.asyncio
    async def test_with_unauthorized_user(
        self, client, test_get_session, test_setup, user
    ):
        """
        Test unblock with unauthorized user
        """

        response = client.delete(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer some_fake_token"},
        )

        assert response.json()["status_code"] == 401
