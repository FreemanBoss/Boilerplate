from tests.conftest_helper import create_login_payload
import pytest

from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles
from api.v1.notification.service import notification_service


class TestNotificationRoute:
    """
    Test class for notification route.
    """

    @pytest.mark.asyncio
    async def test_retrieve_notifications_success(
        self, client, test_setup, mock_notification_creation
    ):
        """
        Test for successful retrieval of notifications by superadmin
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.get(
            url="/api/v1/notifications",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 200

        data = reg_response.json()

        assert data["message"] == "Notifications Fetched Successfully."
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_update_notifications_success(
        self, client, test_setup, mock_notification_creation
    ):
        """
        Test for successful update of notifications by superadmin
        """
        _, notifications = mock_notification_creation

        assert notifications[0].is_read == False

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.put(
            url=f"/api/v1/notifications/{notifications[0].id}",
            json={
                "is_read": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 200

        data = reg_response.json()

        assert data["message"] == "Notification Updated Successfully."
        assert data["data"]["is_read"] == True

    @pytest.mark.asyncio
    async def test_update_notifications_field_validations(
        self, client, test_setup, mock_notification_creation
    ):
        """
        Test for successful validation of notification
        """
        _, notifications = mock_notification_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.put(
            url=f"/api/v1/notifications/{notifications[0].id}",
            json={"is_read": "none"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 422

        data = reg_response.json()

        assert data["message"] == "Validation Error."
        assert (
            data["data"]["msg"]
            == "Input should be a valid boolean, unable to interpret input"
        )

    @pytest.mark.asyncio
    async def test_update_notifications_field_validations_two(
        self, client, test_setup, mock_notification_creation
    ):
        """
        Test for successful validation of notifications field update
        """
        _, notifications = mock_notification_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.put(
            url=f"/api/v1/notifications/{notifications[0].id}",
            json={"wrong": "none"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 422

        data = reg_response.json()

        assert data["message"] == "Validation Error."
        assert data["data"]["msg"] == "Field required"

    @pytest.mark.asyncio
    async def test_retrieve_notifications(
        self, client, test_setup, mock_notification_creation
    ):
        """
        Test for successful fetching of notifications
        """
        _, notifications = mock_notification_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.get(
            url=f"/api/v1/notifications/{notifications[0].id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 200

        data = reg_response.json()

        assert data["message"] == "Notification Retrieved Successfully."
        assert data["data"]["id"] == notifications[0].id
