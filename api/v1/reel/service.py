from api.core.base.services import Service
from api.v1.reel.model import Reel


class ReelService(Service):
    """
    Service class for reels.
    """
    def __init__(self, model) -> None:
        super().__init__(model)


reel_service = ReelService(Reel)
