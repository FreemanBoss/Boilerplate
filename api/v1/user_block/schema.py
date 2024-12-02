"""
pydantic models
"""

import unicodedata
from typing import Optional, Annotated, List
from datetime import datetime, timezone
import time
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    model_validator
)

from api.core.base.responses import BaseResponseData, BaseResponse
from bleach import clean


class UserBlockBase(BaseResponseData):
    """
    UserBlockBase
    """

    id: str = Field(examples=["a0c96829-e826-4ab3-90f6-55b6c9a533bb"])
    blocker_id: str = Field(examples=["a0c96829-e826-4ab3-90s6-55b6c9a533bb"])
    blocked_id: str = Field(examples=["a0c96829-e826-4ab3-90s6-55b6c9a533bb"])
    reason: Optional[str] = Field(examples=["Optional reason for blocking"])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])


class UserBlockCreate(BaseModel):
    """ 
    Schema for user block create request
    """

    reason: Annotated[
        Optional[str],
        StringConstraints(
            max_length=32, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(None, examples=["Optional reason for blocking"])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates reason field
        """
        reason: str = values.get("reason", "")

        if reason:
            validate_fields(reason, "reason")
            values["reason"] = unicodedata.normalize(
                "NFKC", clean(reason.lower())
            ).title()

        return values


class CreateUserBlockResponse(BaseResponse):
    """
    User block response
    """

    status_code: int = Field(examples=[201], default=201)
    data: UserBlockBase


class UserBlockResponse(BaseResponse):
    """
    User block response
    """

    data: UserBlockBase

class AllUserBlockResponse(BaseResponse):
    """
    User block response
    """

    page: int = Field(examples=[1])
    limit: int = Field(examples=[10])
    total_pages: int = Field(examples=[1])
    total_items: int = Field(examples=[20])
    data: List[UserBlockBase]


class DeleteBlockResponse(BaseResponse):
    """
    Delete block response
    """

    message: Optional[str] = Field(
        examples=["User successfully unblocked"],
        default="User successfully unblocked"
    )