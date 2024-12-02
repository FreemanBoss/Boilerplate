import pytest

from api.v1.user.service import user_service

from api.v1.dyt_token.service import (
    dyt_token_service
)



class TestDytTokenService:
    """
    Tests class for dyt_token service.
    """
    @pytest.mark.asyncio
    async def test_create_dyt_token(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create dyt_token.
        """
        mock_johnson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        
        new_dyt_token = await dyt_token_service.create(
            {
                "user_id": johnson_user.id,
            },
            test_get_session
        )
        
        assert new_dyt_token is not None