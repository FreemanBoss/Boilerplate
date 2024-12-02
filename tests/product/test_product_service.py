import pytest

from api.v1.user.service import user_service
from api.v1.product.service import product_service


class TestProductService:
    """
    Tests class for product service.
    """
    @pytest.mark.asyncio
    async def test_create_a_product(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create product.
        """
        mock_johnson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        
        new_product = await product_service.create(
            {
                "creator_id": johnson_user.id,
            },
            test_get_session
        )
        
        assert new_product is not None