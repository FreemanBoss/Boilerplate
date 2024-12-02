from typing import Annotated, Optional
from fastapi import (
    APIRouter,
    status,
    Depends,
    Request,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.auth.dependencies import oauth2_scheme
from api.v1.place.schema import (
    AllPlacesOutSchema,
    FetchPlaceOutputSchema,
    FetchPlaceCategoriesOutputSchema,
)
from api.v1.place.service import place_service


logger = create_logger("Places Route")


place = APIRouter(prefix="/places", tags=["PLACES"])


@place.get(
    "/categories",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=FetchPlaceCategoriesOutputSchema,
)
async def get_place_categories(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    page: Optional[int] = Query(default=1, examples=[1]),
    limit: Optional[int] = Query(default=10, examples=[10]),
):
    """Fetches all Categories linked to places"""
    params = {
        "page": page,
        "limit": limit,
    }
    return await place_service.fetch_place_categories(
        session=session, request=request, access_token=access_token, params=params
    )


@place.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AllPlacesOutSchema,
    responses=responses,
)
async def fetch_all_places(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    page: Optional[int] = Query(default=1, examples=[1]),
    limit: Optional[int] = Query(default=10, examples=[10]),
    category: Optional[str] = Query(default=None, examples=["Restaurant"]),
):
    """
    Fetches all places close to a user location.
    """
    valid_params = {
        "page": page,
        "limit": limit,
        "category": category,
    }
    return await place_service.retrieve_all_places(
        params=valid_params,
        session=session,
        request=request,
        access_token=access_token,
    )


@place.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=AllPlacesOutSchema,
    responses=responses,
)
async def fetch_all_searched_places(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    page: Optional[int] = Query(default=1, examples=[1]),
    limit: Optional[int] = Query(default=10, examples=[10]),
    city: Optional[str] = Query(default=None, examples=["Lagos"]),
    state: Optional[str] = Query(default=None, examples=["Lagos"]),
    country: Optional[str] = Query(default=None, examples=["Nigeria"]),
    category: Optional[str] = Query(default=None, examples=["Restaurant"]),
    place_name: Optional[str] = Query(default=None, examples=["Munchy Kitchen"]),
):
    """
    Fetches all places close to a location or within a specified location
    or the specified place-name.
    """
    valid_params = {
        "page": page,
        "limit": limit,
        "city": city,
        "state": state,
        "country": country,
        "category": category,
        "place_name": place_name,
    }
    return await place_service.retrieve_all_places(
        params=valid_params,
        session=session,
        request=request,
        access_token=access_token,
        search=True,
    )


@place.get(
    "/{place_id}",
    status_code=status.HTTP_200_OK,
    response_model=FetchPlaceOutputSchema,
    responses=responses,
)
async def retrieves_a_specific_place(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    place_id: str,
):
    """Retrieves a specific place."""

    return await place_service.fetch_a_specific_place(
        session=session, request=request, access_token=access_token, place_id=place_id
    )
