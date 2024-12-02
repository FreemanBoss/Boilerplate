from api.core.base.services import Service
from api.v1.activity_log.model import ActivityLog


class ActivityLogService(Service):
    """
    Service class for ActivityLog.
    """
    def __init__(self, model) -> None:
        super().__init__(model)

activity_log_service = ActivityLogService(ActivityLog)
