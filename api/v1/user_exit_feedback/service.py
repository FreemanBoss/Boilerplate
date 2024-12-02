from api.core.base.services import Service
from api.v1.user_exit_feedback.model import (
    UserExitFeedback,
)


class UserExitFeedbackService(Service):
    """
    Service class for user exit feedback.
    """
    def __init__(self, model) -> None:
        super().__init__(model)




user_exit_feedback_service = UserExitFeedbackService(UserExitFeedback)
