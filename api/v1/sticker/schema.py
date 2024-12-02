from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------------
# Single sticker
class StickerBase(BaseModel):
    """
    Sticker base schema
    """

    id: str = Field(examples=["1231231-342342-542543-534566"])
    name: str = Field(examples=["oxygen"])
    price: float = Field(examples=[12.3])
    url: str = Field(examples=["http://com.com"])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)


class StickerOutSchema(BaseModel):
    """
    Schema for sticker output
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Sticker retrieved successfully.",
        examples=["Sticker retrieved successfully."],
    )
    data: StickerBase


# -----------------------------------------------------------
# exchangedStickers


class ExchangedStickerBase(BaseModel):
    """
    Sticker base schema
    """

    id: str = Field(examples=["1231231-342342-542543-534566"])
    name: str = Field(examples=["oxygen"])
    price: float = Field(examples=[12.3])
    url: str = Field(examples=["http://com.com"])
    total_quantity: int = Field(examples=[23])


class UserStickerOutSchema(BaseModel):
    """
    Schema for sticker output
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Stickers retrieved successfully.",
        examples=["Stickers retrieved successfully."],
    )
    data: List[Optional[ExchangedStickerBase]]
