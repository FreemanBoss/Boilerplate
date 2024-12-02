import pytest

from api.v1.user.service import user_service
from api.v1.user_device.service import user_device_service
from api.v1.activity_log.service import activity_log_service


class TestActivityLogService:
    """
    Tests class for activity-log service.
    """

    @pytest.mark.asyncio
    async def test_create_activity_log(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating activity_log.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_johnson_user_dict.pop("confirm_password")
        # admin user johnson
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        new_user_device = await user_device_service.create(
            {"user_id": johnson_user.id, "device_token": "some token1"},
            test_get_session,
        )

        assert new_user_device is not None

        new_user_device_two = await user_device_service.create(
            {"user_id": jayson_user.id, "device_token": "some token2"}, test_get_session
        )

        assert new_user_device_two is not None

        jayson_activity = await activity_log_service.create(
            {
                "user_id": jayson_user.id,
                "target_user_id": johnson_user.id,
                "device_id": new_user_device.id,
                "action_type": "like photo",
                "ip_address": "some ip",
            },
            test_get_session,
        )

        assert jayson_activity is not None
