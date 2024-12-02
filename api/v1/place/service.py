import math
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError

from api.core.base.services import Service
from api.v1.place.model import Place, PlaceCategory
from api.v1.place.schema import (
    AllPlacesOutSchema,
    FetchPlaceOutputSchema,
    FetchPlaceCategoriesOutputSchema,
    PlaceBase,
    PlacecategoryBase,
)
from api.v1.auth.dependencies import (
    verify_token,
    authenticate_premium_user,
)
from api.utils.validate_pagination import validate_pagination
from api.v1.location.model import Location, PlaceLocation
from api.v1.location.service import user_location_service, place_location_service


class PlaceService(Service):
    """
    Service class for place.
    """

    def __init__(self, model) -> None:
        super().__init__(model)

    async def fetch_place_categories(
        self,
        session: AsyncSession,
        request: Request,
        access_token: str,
        params: dict,
    ) -> Optional[FetchPlaceCategoriesOutputSchema]:
        """
        Retrieves categories linked to places.l

        Args:
            session(AsyncSession): database session object
            request(Request): request object
            access_token(str): access_token from Authorization Header
        Returns:
            FetchPlaceCategoriesOutputSchema(pydantic): all categories.
        """
        _ = await verify_token(token=access_token, request=request, token_type="access")
        where = await validate_pagination(params)

        categories = await place_category_service.fetch_all(
            filterer={}, session=session, where=where
        )

        return FetchPlaceCategoriesOutputSchema(
            data=[
                PlacecategoryBase.model_validate(category, from_attributes=True)
                for category in categories
            ]
        )

    async def retrieve_all_places(
        self,
        session: AsyncSession,
        request: Request,
        access_token: str,
        params: dict,
        search: bool = False,
    ) -> Optional[AllPlacesOutSchema]:
        """
        Fetches all places close to a location a role.

         Args:
             session(AsyncSession): database session object
             request(Request): request object
             access_token(str): access_token from Authorization Header.
             params(dict): the pagination and query parameters.
         Returns:
             AllPlacesOutSchema(object): All places.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )

        # validate category
        params_category = params.get("category")
        if not params_category:
            raise RequestValidationError(
                errors=["Category is missing in the query parameters."]
            )
        category = await place_category_service.fetch(
            {"name": params_category.title()}, session
        )
        if not category:
            raise HTTPException(status_code=400, detail="Category does not exist.")

        # validate and sort params
        filtered_params = await validate_pagination(params)
        params_copy = filtered_params.copy()

        # Base Query
        stmt = select(Place).where(Place.category_id == category.id)

        # Filter by user’s current location if not in search mode
        # user location
        location = await user_location_service.get_current_location(
            session, claims.get("user_id", "")
        )
        if not location:
            raise HTTPException(
                status_code=400, detail="User does not have a location yet."
            )
        if not search:

            stmt = stmt.join(
                PlaceLocation, PlaceLocation.location_id == location.id
            ).where(PlaceLocation.location_id == location.id)

        if search:

            # Apply dynamic filtering for search
            if params.get("city"):
                if location.city != params.get("city").title():
                    _ = await authenticate_premium_user(
                        user_id=claims.get("user_id", ""), session=session
                    )
                stmt = stmt.join(PlaceLocation).where(
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
            if params.get("place_name"):
                _ = await authenticate_premium_user(
                    user_id=claims.get("user_id", ""), session=session
                )
                stmt = stmt.where(Place.name.ilike(f"%{params['place_name']}%"))

        # Execute the statement and get total count for pagination
        result = await session.execute(stmt)
        all_places = result.scalars().all()
        print([pl.name for pl in all_places])

        count_stmt = (
            select(func.count())
            .select_from(Place)
            .where(Place.category_id == category.id)
        )
        if not search:
            count_stmt = count_stmt.where(PlaceLocation.location_id == location.id)
        count_result = await session.execute(count_stmt)
        total_items = count_result.scalar() or 0

        total_pages = 0
        if total_items > 0:
            total_pages = math.ceil(total_items / params_copy["limit"])

        return AllPlacesOutSchema(
            page=params_copy["page"],
            limit=params_copy["limit"],
            total_items=total_items,
            total_pages=total_pages,
            data=[
                PlaceBase.model_validate(place, from_attributes=True)
                for place in all_places
            ],
        )

    async def fetch_a_specific_place(
        self, session: AsyncSession, request: Request, access_token: str, place_id: str
    ) -> Optional[FetchPlaceOutputSchema]:
        """
        Retrieves a specific place.

        Args:
            session(AsyncSession): database session object
            request(Request): request object
            access_token(str): access_token from Authorization Header.
            place_id(str): the id of the place to retrieve.
        Returns:
            FetchPlaceOutputSchema(object): A specific place.
        """
        claims: dict | None = await verify_token(
            token=access_token, request=request, token_type="access"
        )

        found_place = await self.fetch({"id": place_id}, session)
        if not found_place:
            raise HTTPException(status_code=400, detail="Place not found")
        if not await self.check_user_location_match_place_location(
            session, claims.get("user_id", ""), place_id
        ):
            _ = await authenticate_premium_user(
                user_id=claims.get("user_id", ""), session=session
            )

        return FetchPlaceOutputSchema(
            data=PlaceBase.model_validate(found_place, from_attributes=True)
        )

    async def check_user_location_match_place_location(
        self, session: AsyncSession, user_id: str, place_id: str
    ) -> bool:
        """
        Checks if a user_location place_location are the same.

        Args:
            session (AsyncSession): The database session.
            user_id (str): The ID of the user.
            place_id (str): The ID of the place.

        Returns:
            bool: True if the user has access; otherwise, raises HTTPException.

        Raises:
            HTTPException: 401 Unauthorized if the user does not have access.
        """

        # Retrieve user's current location
        user_location_exist = await user_location_service.fetch(
            {"user_id": user_id, "is_current": True}, session
        )

        if not user_location_exist:
            raise HTTPException(
                status_code=401, detail="User does not have a registered location."
            )

        # Retrieve place's location
        place_location_exist = await place_location_service.fetch(
            {"place_id": place_id}, session
        )

        if not place_location_exist:
            raise HTTPException(status_code=404, detail="Place location not found.")

        return user_location_exist.location_id == place_location_exist.location_id


class PlacecategoryService(Service):
    """
    Place-category service class
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


place_service = PlaceService(Place)
place_category_service = PlacecategoryService(PlaceCategory)
