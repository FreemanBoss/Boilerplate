from api.core.base.services import Service
from api.v1.date_invitation.model import DateInvitation, Booking
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from api.v1.place.model import Place

class DateBookingService(Service):
    """
    Service class for handling place-related functionalities, such as booking and cancellation.
    """
    def __init__(self, model) -> None:
        super().__init__(model)

    async def book_for_self(self, user_id: str, place_id: str, session: AsyncSession) -> Booking:
        """
        Books a date for a single individual.
        :param user_id: ID of the user booking the date
        :param place_id: ID of the place being booked
        :param session: SQLAlchemy AsyncSession
        :return: Booking object
        """
        place = await self.fetch({"id": place_id}, session)
        if not place:
            raise ValueError("Place not found")

        existing_booking = await self.fetch({"user_id": user_id, "place_id": place_id}, session)
        if existing_booking:
            raise ValueError("You already have a booking for this place")

        booking = Booking(user_id=user_id, place_id=place_id)
        session.add(booking)
        await session.commit()

        return booking

    async def book_for_two(self,
        user_id_1: str,
        user_id_2: str,
        place_id: str,
        session: AsyncSession) -> Booking:
        """
        Books a date for two individuals.
        :param user_id_1: ID of the first user
        :param user_id_2: ID of the second user
        :param place_id: ID of the place being booked
        :param session: SQLAlchemy AsyncSession
        :return: Booking object
        """

        place = await self.fetch({"id": place_id}, session)
        if not place:
            raise ValueError("Place not found")

        existing_booking = await self.fetch({"user_id": user_id_1, "place_id": place_id}, session)
        if existing_booking:
            raise ValueError(f"User {user_id_1} already has a booking for this place")

        existing_booking = await self.fetch({"user_id": user_id_2, "place_id": place_id}, session)
        if existing_booking:
            raise ValueError(f"User {user_id_2} already has a booking for this place")

        booking_1 = Booking(user_id=user_id_1, place_id=place_id)
        booking_2 = Booking(user_id=user_id_2, place_id=place_id)
        session.add(booking_1)
        session.add(booking_2)
        await session.commit()

        return booking_1, booking_2

    async def cancel_date(self, booking_id: int, session: AsyncSession) -> bool:
        """
        Cancels an existing booking by its ID.
        :param booking_id: ID of the booking to cancel
        :param session: SQLAlchemy AsyncSession
        :return: True if cancellation was successful, else False
        """
        booking = await self.fetch({"id": booking_id}, session)
        if not booking:
            raise ValueError("Booking not found")

        stmt = delete(Booking).where(Booking.id == booking_id)
        result = await session.execute(stmt)
        await session.commit()
        
        return result.rowcount > 0

    async def edit_booking(
        self, booking_id: int, new_user_id: int, session: AsyncSession
    ) -> Booking:
        """
        Edits an existing booking by changing the user.
        :param booking_id: ID of the booking to edit
        :param new_user_id: New user ID to associate with the booking
        :param session: SQLAlchemy AsyncSession
        :return: The updated Booking object
        """
        booking = await self.fetch({"id": booking_id}, session)
        if not booking:
            raise ValueError("Booking not found")

        existing_booking = await self.fetch({"user_id": new_user_id,
            "place_id": booking.place_id}, session)
        if existing_booking:
            raise ValueError("The new user already has a booking for this place")

        booking.user_id = new_user_id
        await session.commit()

        return booking

date_booking_service = DateBookingService(Place)
