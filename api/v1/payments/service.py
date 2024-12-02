from api.core.base.services import Service
from api.v1.payments.model import Payment


class PaymentService(Service):
    """
    Service class for Payment resource.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

payment_service = PaymentService(Payment)
