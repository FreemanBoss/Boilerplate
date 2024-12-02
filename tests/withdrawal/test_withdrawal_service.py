import pytest

from api.v1.user.service import user_service

from api.v1.withdrawal.service import (
    withdrawal_service,
    
)


class TestWithdrawalService:
    """
    Tests class for withdarwal service.
    """
    @pytest.mark.asyncio
    async def test_create_withdarwal(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create withdrawal.
        """
        mock_johnson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        
        new_withdrawal = await withdrawal_service.create(
            {
                "user_id": johnson_user.id,
                "amount": 1000,
                "status": "pending",
            },
            test_get_session
        )
        
        assert new_withdrawal is not None
    