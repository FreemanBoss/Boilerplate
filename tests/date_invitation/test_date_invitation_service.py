import pytest
from datetime import date

from api.v1.user.service import user_service

from api.v1.date_invitation.service import (
    date_invitation_service,
)



class TestDateInvitationService:
    """
    Tests class for date_invitation service.
    """
    @pytest.mark.asyncio
    async def test_create_date_invitation(self,
                               mock_johnson_user_dict,
                               mock_jayson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create date_invitation.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        jayson_user = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        
        new_invitation = await date_invitation_service.create(
            {
                "inviter_id": johnson_user.id,
                "invitee_id": jayson_user.id,
                "status": "pending",
                "date_time": date(2024, 12, 1),
                "destination": "Lagos"
            },
            test_get_session
        )
        
        assert new_invitation is not None