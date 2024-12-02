from api.core.base.services import Service
from api.v1.gift.model import (
    Gift,
    ExchangedGift,
)


class GiftService(Service):
    """
    Service class for gifts.
    """
    def __init__(self, model) -> None:
        super().__init__(model)\


class ExchangedGiftService(Service):
    """
    Service class for gifts.
    """
    def __init__(self, model) -> None:
        super().__init__(model)



gift_service = GiftService(Gift)
exchanged_gift_service = ExchangedGiftService(ExchangedGift)
