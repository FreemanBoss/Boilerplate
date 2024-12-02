from api.core.base.services import Service
from api.v1.dyt_token.model import DytToken


class DytTokenService(Service):
    """
    Service class for dyttoken.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

dyt_token_service = DytTokenService(DytToken)
