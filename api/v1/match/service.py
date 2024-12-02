from api.core.base.services import Service
from api.v1.match.model import Match


class MatchService(Service):
    """
    Service class for match.
    """
    def __init__(self, model) -> None:
        super().__init__(model)


match_service = MatchService(Match)
