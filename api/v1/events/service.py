import math
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError

from api.core.base.services import Service
from api.v1.events.model import Event, EventTicket
from api.v1.events.schema import (
    AllEventsOutSchema,
    FetchEventDetailSchema,
    FetchEventTicketSchema,
    EventBase,
    EventTicketBase,
)
from api.v1.auth.dependencies import (
    verify_token,
    authenticate_premium_user,
)
from api.utils.validate_pagination import validate_pagination
from api.v1.location.model import Location, EventLocation
from api.v1.location.service import user_location_service, event_location_service


class EventService(Service):
    """
    Service class for event-related functionalities.
    """

    def __init__(self, model) -> None:
        super().__init__(model)

    async def search_events(self, session: AsyncSession, search_params: dict):
        """
        Search for events based on provided search parameters.

        Args:
            session (AsyncSession): Database session object.
            search_params (dict): Parameters to filter the search.

        Returns:
            List[Event]: Matching events.
        """
        stmt = select(Event)

        # Apply search filters
        if "event_name" in search_params:
            stmt = stmt.where(Event.name.ilike(f"%{search_params['event_name']}%"))
        if "city" in search_params:
            stmt = stmt.join(Location).where(Location.city == search_params["city"])
        if "state" in search_params:
            stmt = stmt.join(Location).where(Location.state == search_params["state"])
        if "country" in search_params:
            stmt = stmt.join(Location).where(Location.country == search_params["country"])

        result = await session.execute(stmt)
        return result.scalars().all()

    async def fetch_event_tickets(
        self,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[FetchEventTicketSchema]:
        """
        Retrieves tickets linked to events.

        Args:
            session(AsyncSession): database session object
            request(Request): request object
            access_token(str): access_token from Authorization Header
        Returns:
            FetchEventTicketSchema(pydantic): all ies.
        """
        _ = await verify_token(token=access_token, request=request, token_type="access")
        where = await validate_pagination()

        tickets = await event_ticket_service.fetch_all(
            filterer={}, session=session, where=where
        )

        return FetchEventTicketSchema(
            data=[
                EventTicketBase.model_validate(tickets, from_attributes=True)
                for ticket in tickets
            ]
        )

    async def retrieve_all_events(
        self,
        session: AsyncSession,
        request: Request,
        access_token: str,
        params: dict,
        search: bool = False,
    ) -> Optional[AllEventsOutSchema]:
        """
        Fetches all events close to a location or based on search criteria.

         Args:
             session(AsyncSession): database session object
             request(Request): request object
             access_token(str): access_token from Authorization Header.
             params(dict): the pagination and query parameters.
         Returns:
             AllEventsOutSchema(object): All events.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )

        params_ticket = params.get("ticket")
        if not params_ticket:
            raise RequestValidationError(
                errors=["Ticket is missing in the query parameters."]
            )
        ticket = await event_ticket_service.fetch(
            {"name": params_ticket.title()}, session
        )
        if not ticket:
            raise HTTPException(status_code=400, detail="ticket does not exist.")

        filtered_params = await validate_pagination(params)
        params_copy = filtered_params.copy()

        stmt = select(Event).where(Event.ticket_id == ticket.id)

        location = await user_location_service.get_current_location(
            session, claims.get("user_id", "")
        )
        if not location:
            raise HTTPException(
                status_code=400, detail="User does not have a location yet."
            )
        if not search:

            stmt = stmt.join(
                EventLocation, EventLocation.location_id == location.id
            ).where(EventLocation.location_id == location.id)

        if search:

            if params.get("city"):
                if location.city != params.get("city").title():
                    _ = await authenticate_premium_user(
                        user_id=claims.get("user_id", ""), session=session
                    )
                stmt = stmt.join(EventLocation).where(
                    Location.city == params["city"].title()
                )
            if params.get("state"):
                if location.city != params.get("state").title():
                    _ = await authenticate_premium_user(
                        user_id=claims.get("user_id", ""), session=session
                    )
                stmt = stmt.where(Location.state == params["state"].title())
            if params.get("country"):
                if location.city != params.get("country").title():
                    _ = await authenticate_premium_user(
                        user_id=claims.get("user_id", ""), session=session
                    )
                stmt = stmt.where(Location.country == params["country"].title())
            if params.get("event_name"):
                _ = await authenticate_premium_user(
                    user_id=claims.get("user_id", ""), session=session
                )
                stmt = stmt.where(Event.name.ilike(f"%{params['event_name']}%"))

        result = await session.execute(stmt)
        all_events = result.scalars().all()

        count_stmt = (
            select(func.count())
            .select_from(Event)
            .where(Event.ticket_id == ticket.id)
        )
        if not search:
            count_stmt = count_stmt.where(EventLocation.location_id == location.id)
        count_result = await session.execute(count_stmt)
        total_items = count_result.scalar() or 0

        total_pages = 0
        if total_items > 0:
            total_pages = math.ceil(total_items / params_copy["limit"])

        return AllEventsOutSchema(
            page=params_copy["page"],
            limit=params_copy["limit"],
            total_items=total_items,
            total_pages=total_pages,
            data=[
                EventBase.model_validate(event, from_attributes=True)
                for event in all_events
            ],
        )

    async def fetch_a_specific_event(
        self, session: AsyncSession, request: Request, access_token: str, event_id: str
    ) -> Optional[FetchEventDetailSchema]:
        """
        Retrieves a specific event.

        Args:
            session(AsyncSession): database session object
            request(Request): request object
            access_token(str): access_token from Authorization Header.
            event_id(str): the id of the event to retrieve.
        Returns:
            FetchEventDetailSchema(object): A specific event.
        """
        claims: dict | None = await verify_token(
            token=access_token, request=request, token_type="access"
        )

        found_event = await self.fetch({"id": event_id}, session)
        if not found_event:
            raise HTTPException(status_code=400, detail="Event not found")
        if not await self.check_user_location_match_event_location(
            session, claims.get("user_id", ""), event_id
        ):
            _ = await authenticate_premium_user(
                user_id=claims.get("user_id", ""), session=session
            )

        return FetchEventDetailSchema(
            data=EventBase.model_validate(found_event, from_attributes=True)
        )

    async def check_user_location_match_event_location(
        self, session: AsyncSession, user_id: str, event_id: str
    ) -> bool:
        """
        Checks if a user_location and event_location are the same.

        Args:
            session (AsyncSession): The database session.
            user_id (str): The ID of the user.
            event_id (str): The ID of the event.

        Returns:
            bool: True if the user has access; otherwise, raises HTTPException.

        Raises:
            HTTPException: 401 Unauthorized if the user does not have access.
        """

        user_location_exist = await user_location_service.fetch(
            {"user_id": user_id, "is_current": True}, session
        )

        if not user_location_exist:
            raise HTTPException(
                status_code=401, detail="User does not have a registered location."
            )

        # Retrieve event's location
        event_location_exist = await event_location_service.fetch(
            {"event_id": event_id}, session
        )

        if not event_location_exist:
            raise HTTPException(status_code=404, detail="Event location not found.")

        return user_location_exist.location_id == event_location_exist.location_id


class EventTicketService(Service):
    """
    Event-ticket service class
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


event_service = EventService(Event)
event_ticket_service = EventTicketService(EventTicket)
