from api.core.base.services import Service
from api.v1.wallet.model import Wallet


class WalletService(Service):
    """
    Service class for Wallet resource.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

wallet_service = WalletService(Wallet)
