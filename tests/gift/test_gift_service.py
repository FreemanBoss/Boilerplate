import pytest

from api.v1.user.service import user_service

from api.v1.gift.service import (
    gift_service,
    exchanged_gift_service
)



class TestGiftService:
    """
    Tests class for gift service.
    """
    @pytest.mark.asyncio
    async def test_create_gift(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create gift.
        """
        mock_johnson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        
        new_gift = await gift_service.create(
            {
                "name": "new-gift",
                "currency": "USD",
                "price": 5.0,
                "creator_id": johnson_user.id
            },
            test_get_session
        )
        
        assert new_gift is not None

    @pytest.mark.asyncio
    async def test_create_exchanged_gift(self,
                               mock_johnson_user_dict,
                               mock_jayson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create exchanged_gift.
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
        
        new_gift = await gift_service.create(
            {
                "name": "new-gift",
                "currency": "USD",
                "price": 5.0,
                "creator_id": johnson_user.id
            },
            test_get_session
        )
        
        assert new_gift is not None
        
        new_exchanged_gift = await exchanged_gift_service.create(
            {
                "sender_id": johnson_user.id,
                "receiver_id": jayson_user.id,
                "gift_id": new_gift.id,
            },
            test_get_session
        )
        
        assert new_exchanged_gift is not None
        assert new_exchanged_gift.sender_id == johnson_user.id