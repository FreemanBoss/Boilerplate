from typing import List, Optional
from datetime import datetime, timezone, time
from pydantic import BaseModel, Field, ConfigDict


class PlaceBase(BaseModel):
    """
    Schema base for verification.
    """

    id: str = Field(examples=["1234-567890987766-5554325346346-43767465"])
    name: str = Field(examples=["The Grand Restaurant"])

    banner: dict = Field(
        examples=[{"banner_1": "https://aws.com/photos/banner/grand_restaurant.png"}]
    )
    rating: int = Field(examples=[4])
    about: Optional[str] = Field(examples=["Photo Irregularity."])
    menu_url: str = Field(examples=["https://aws.com/photos/menu/grand_restaurant.png"])
    opening_hour: time = Field(examples=[time(9, 00)])
    closing_hour: time = Field(examples=[time(21, 00)])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------


class AllPlacesOutSchema(BaseModel):
    """
    Schema for places response
    """

    status_code: int = Field(default=200, examples=[200])
    page: int
    limit: int
    total_pages: int
    total_items: int
    message: str = Field(
        default="Places Retrieved Successfully.",
        examples=["Places Retrieved Successfully."],
    )
    data: List[PlaceBase]


# ----------------------------------------------------------------
class FetchPlaceOutputSchema(BaseModel):
    """
    Schema for fetching a single place.
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Place retrieved Successfully.",
        examples=["Place retrieved Successfully."],
    )
    data: PlaceBase


# -------------------------------------------------------
class PlacecategoryBase(BaseModel):
    """
    Schema for place categories.
    """

    id: str = Field(examples=["213123-1324234-25345-23423143"])
    name: str = Field(examples=["Restaurant"])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)


class FetchPlaceCategoriesOutputSchema(BaseModel):
    """
    Schema for fetching place_categories response
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Place-Categories Retrieved Successfully.",
        examples=["Place-Categories Retrieved Successfully."],
    )
    data: List[PlacecategoryBase]
