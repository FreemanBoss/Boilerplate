from tests.conftest_helper import create_login_payload
import pytest


class TestBlockUserEndpoints:
    """
    Test class for the integration of the user block route.
    """

    @pytest.mark.asyncio
    async def test_block_user_then_get_blocked_then_unblock_then_get_blocked_success(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test blocking a user
            - Then get all blocked to make sure only that one blocked user is returned
            - Then unblock the user
            - Then get all blocked to make sure no user is returned
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # block superadmin
        response = client.post(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "User successfully blocked."
        assert response.json()["data"]["blocker_id"] == jayson_user.id
        assert response.json()["data"]["blocked_id"] == johnson_superadmin.id

        # get all blocked to make sure it's only superadmin
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

        # Unblock superadmin
        response = client.delete(
            url=f"/api/v1/profiles/settings/block-lists/{johnson_superadmin.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "User successfully unblocked"

        # Get all blocked users (should be empty)
        response = client.get(
            url=f"/api/v1/profiles/settings/block-lists",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(response.json())

        assert response.json()["status_code"] == 200
        assert response.json()["message"] == "Blocked list successfully generated"
        assert response.json()["total_items"] == 0
        assert response.json()["data"] == []
