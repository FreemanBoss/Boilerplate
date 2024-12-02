from api.core.base.services import Service
from api.v1.withdrawal.model import Withdrawal


class WithdrawalService(Service):
    """
    Service class for Withdrawal resource.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

withdrawal_service = WithdrawalService(Withdrawal)
