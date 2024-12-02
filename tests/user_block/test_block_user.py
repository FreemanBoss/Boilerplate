from tests.conftest_helper import create_login_payload
import pytest


class TestBlockUser:
    """
    Test class for user block route.
    """

    @pytest.mark.asyncio
    async def test_block_user_success(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful block
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # test user, user should block test user superadmin
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "User successfully blocked."
        assert response.json()["data"]["blocker_id"] == jayson_user.id
        assert response.json()["data"]["blocked_id"] == johnson_superadmin.id

    @pytest.mark.asyncio
    async def test_block_yourself(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for blocking oneself
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # test user blocking user
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 400
        assert response.json()["message"] == "Cannot block yourself"

    @pytest.mark.asyncio
    async def test_block_non_existing_user(
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

        # test blocking non existing user is
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{"some_fake_id"}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 404
        assert response.json()["message"] == "User to block not found"

    @pytest.mark.asyncio
    async def test_block_user_twice(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test blocking the same user twice
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # user blocks superadmin
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "User successfully blocked."
        assert response.json()["data"]["blocker_id"] == jayson_user.id
        assert response.json()["data"]["blocked_id"] == johnson_superadmin.id

        # user blocks superadmin again
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 400
        assert response.json()["message"] == "User is already blocked"

    @pytest.mark.asyncio
    async def test_with_unauthorized_user(
        self, client, test_get_session, test_setup, user
    ):
        """
        Test block with unauthorized user
        """

        response = client.delete(
            url=f"/api/v1/profiles/settings",
            headers={"Authorization": f"Bearer some_fake_token"},
        )

        assert response.json()["status_code"] == 401
