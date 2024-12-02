"""
pydantic models
"""

from fastapi import File, UploadFile
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, validator

from api.core.base.responses import BaseResponseData, BaseResponse


class ProfilePhotoBase(BaseResponseData):
    """
    ProfilePhotoBase
    """

    id: str = Field(examples=["a0c96829-e826-4ab3-90f6-55b6c9a533bb"])
    user_id: str = Field(examples=["a0c96829-e826-4ab3-90s6-55b6c9a533bb"])
    url: str = Field(examples=["some_random_url"])
    is_primary: Optional[bool] = Field(examples=[False])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)


class CreateProfilePhotoRequest(BaseModel):
    """
    Request schema for creating a user's profile photos.
    """

    photos: List[UploadFile] = File(
        ..., description="List of profile photos (4-6 images)"
    )

    @validator("photos")
    def validate_photo_count(cls, v):
        if len(v) < 4 or len(v) > 6:
            raise ValueError("You must provide between 4 and 6 profile photos")
        return v


class CreateProfilePhotoResponse(BaseResponse):
    """
    Response schema for creating a user's profile photos.
    """

    status_code: int = Field(examples=[201], default=201)
    data: List[ProfilePhotoBase]


# -------------------------------------------------------------------
# Replace profile photo
class ReplaceProfilePhotoRequest(BaseModel):
    """
    Request schema for replacing a user's profile photos.
    """

    photo: UploadFile = File(description="List of profile photos (4-6 images)")


class ReplaceProfilePhotoResponse(BaseModel):
    """
    Response schema for replacing a user's profile photos.
    """

    status_code: int = Field(examples=[201], default=201)
    message: str = Field(
        examples=["photo replaced successfully"], default="photo replaced successfully"
    )
    data: ProfilePhotoBase
