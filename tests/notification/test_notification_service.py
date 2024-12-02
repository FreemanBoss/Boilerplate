import pytest
from datetime import datetime, timezone

from api.v1.user.service import user_service

from api.v1.notification.service import notification_service, push_notification_service
from api.v1.user_device.service import user_device_service


class TestNotificationService:
    """
    Tests class for notification service.
    """

    @pytest.mark.asyncio
    async def test_create_notification(
        self,
        mock_johnson_user_dict,
        mock_jayson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for create notification.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        mock_jayson_user_dict.pop("confirm_password")

        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        user_device = await user_device_service.create(
            {
                "user_id": johnson_user.id,
                "device_token": "new token",
                "device_type": "new type",
            },
            test_get_session,
        )

        assert user_device is not None

        new_notification = await notification_service.create(
            {
                "user_id": jayson_user.id,
                "notification_type": "message",
                "message": "it's about to go down.",
                "status": "sent",
                "title": "sometitle",
            },
            test_get_session,
        )

        assert new_notification is not None

        new_push_notification = await push_notification_service.create(
            {
                "user_id": jayson_user.id,
                "device_token_id": user_device.device_token,
                "notification_id": new_notification.id,
                "status": "pending",
                "retry_count": 0,
                "last_attempt_at": datetime.now(timezone.utc),
            },
            test_get_session,
        )

        assert new_push_notification is not None
