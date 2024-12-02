import pytest
from datetime import datetime, timezone

from api.v1.user.service import user_service

from api.v1.wallet.service import (
    wallet_service,
    
)


class TestWalletService:
    """
    Tests class for wallet service.
    """
    @pytest.mark.asyncio
    async def test_create_wallet(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create wallet.
        """
        mock_johnson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        
        new_wallet = await wallet_service.create(
            {
                "user_id": johnson_user.id,
                "balance": 1000,
                "currency": "USD",
            },
            test_get_session
        )
        
        assert new_wallet is not None
    