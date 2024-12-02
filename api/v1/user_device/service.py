from api.core.base.services import Service
from api.v1.user_device.model import UserDevice


class UserDeviceService(Service):
    """
    Service class for user_device resurce
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

user_device_service = UserDeviceService(UserDevice)
