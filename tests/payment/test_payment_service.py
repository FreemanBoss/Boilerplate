import pytest

from api.v1.user.service import user_service

from api.v1.payments.service import payment_service


class TestPaymentService:
    """
    Tests class for payment service.
    """
    @pytest.mark.asyncio
    async def test_create_payment(self,
                               mock_jayson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create payment.
        """
        
        mock_jayson_user_dict.pop("confirm_password")
        
        jayson_user = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        
        new_payment = await payment_service.create(
            {
                "payer_id": jayson_user.id,
                "transaction_id": "some stripe id",
                "payment_for": "event",
                "amount": 34.9,
                "currency": "USD",
                "status": "success",
                "payment_provider": "stripe",
                "payer": "user"
            },
            session=test_get_session
        )
        
        assert new_payment is not None
