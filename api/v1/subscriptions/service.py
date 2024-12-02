from api.core.base.services import Service
from api.v1.subscriptions.model import (
    Subscription,
    SubscriptionPlan,
)

class SubscriptionService(Service):
    """
    Service class for subscription.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


class SubscriptionPlanService(Service):
    """
    Service class for subscription_plan.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

subscription_service = Service(Subscription)
subscription_plan_service = Service(SubscriptionPlan)
