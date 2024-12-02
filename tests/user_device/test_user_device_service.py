
import pytest

from api.v1.user.service import user_service
from api.v1.user_device.service import user_device_service




class TestUserDeviceService:
    """
    Tests class for user_device service.
    """
    @pytest.mark.asyncio
    async def test_create_user_device(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for creating user_device.
        """
        mock_johnson_user_dict.pop("confirm_password")
        # admin user johnson
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        new_user_device = await user_device_service.create(
            {
                "user_id": johnson_user.id,
                "device_token": "some token",
            },
            test_get_session
        )

        assert new_user_device is not None
