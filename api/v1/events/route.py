from typing import Annotated, Optional
from fastapi import APIRouter, status, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.auth.dependencies import oauth2_scheme
from api.v1.events.schema import (
    EventBase,
    EventTicketBase,
    AllEventsOutSchema,
    SearchEventsOutSchema,
    FetchEventDetailSchema,
    FetchEventTicketSchema,
    BookEventTicketResponseSchema,
    BookEventTicketSchema
)
from api.v1.events.service import event_service

logger = create_logger("Events Route")

event = APIRouter(prefix="/events", tags=["EVENTS"])

@event.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AllEventsOutSchema,
    responses=responses,
)
async def fetch_all_events(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    city: Optional[str] = Query(default=None, examples=["New York"]),
    state: Optional[str] = Query(default=None, examples=["NY"]),
    country: Optional[str] = Query(default=None, examples=["USA"]),
    ticket: Optional[str] = Query(default=None, examples=["VIP"]),
    page: Optional[int] = Query(default=1, examples=[1]),
    limit: Optional[int] = Query(default=10, examples=[10]),
):
    valid_params = {
        "page": page,
        "limit": limit,
        "city": city,
        "state": state,
        "country": country,
        "ticket": ticket,  # Include ticket in valid_params
    }
    return await event_service.retrieve_all_events(
        params=valid_params,
        session=session,
        request=request,
        access_token=access_token,
)

@event.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=SearchEventsOutSchema,
    responses=responses,
)
async def search_events_by_term(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    search_term: str,
    city: Optional[str] = Query(default=None, examples=["New York"]),
    state: Optional[str] = Query(default=None, examples=["NY"]),
    country: Optional[str] = Query(default=None, examples=["USA"]),
    page: Optional[int] = Query(default=1, examples=[1]),
    limit: Optional[int] = Query(default=10, examples=[10]),
):
    """
    Retrieves events matching a search term within the user’s location or specified location.
    Premium users can change their location.
    """
    valid_params = {
        "page": page,
        "limit": limit,
        "city": city,
        "state": state,
        "country": country,
        "search_term": search_term,
    }
    return await event_service.search_events(
        params=valid_params,
        session=session,
        request=request,
        access_token=access_token,
    )

# Route 3: Get details of a specific event
@event.get(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=FetchEventDetailSchema,
    responses=responses,
)
async def retrieve_event_details(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    event_id: str,
):
    """
    Retrieves the details of a specific event, including ticket buyers.
    """
    return await event_service.fetch_event_details(
        session=session, request=request, access_token=access_token, event_id=event_id
    )

@event.post(
    "/{event_id}/ticket",
    status_code=status.HTTP_201_CREATED,
    response_model=BookEventTicketSchema,
    responses=responses,
)
async def book_event_ticket(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    event_id: str,
):
    """
    Books an event ticket for a specified event.
    """
    return await event_service.book_ticket_for_event(
        session=session, request=request, access_token=access_token, event_id=event_id
    )

# Route 5: Retrieve a purchased event ticket (GET)
@event.get(
    "/{event_id}/ticket/{ticket_id}",
    status_code=status.HTTP_200_OK,
    response_model=FetchEventTicketSchema,
    responses=responses,
)
async def retrieve_event_ticket(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    event_id: str,
    ticket_id: str,
):
    """
    Retrieves details of a purchased ticket for a specific event.
    """
    return await event_service.fetch_event_ticket_details(
        session=session,
        request=request,
        access_token=access_token,
        event_id=event_id,
        ticket_id=ticket_id,
    )
