from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.core.base.services import Service
from api.v1.location.model import Location, UserLocation, PlaceLocation, EventLocation


class LocationService(Service):
    """
    Service class for location.
    """

    def __init__(self, model) -> None:
        super().__init__(model)


class UserLocationService(Service):
    """
    Class service for user_location.
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

    async def get_current_location(
        self, session: AsyncSession, user_id: int
    ) -> Optional[Location]:
        """
        Retrieves the current user_location.

        Args:
            session(Asyncsession): The database async session object.
            user_id(str): The user to retrieve its location.
        Returns:
            location(Location): the location of the user if found or None.
        """
        stmt = (
            select(Location)
            .join(UserLocation)
            .where(UserLocation.user_id == user_id, UserLocation.is_current == True)
        )
        result = await session.execute(stmt)
        return result.scalar()


class EventLocationService(Service):
    """
    Place-location service class
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


class PlaceLocationService(Service):
    """
    Place-location service class
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


place_location_service = PlaceLocationService(PlaceLocation)

event_location_service = EventLocationService(EventLocation)
location_service = LocationService(Location)
user_location_service = UserLocationService(UserLocation)
