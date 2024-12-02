"""
pydantic models
"""

from typing import Optional, Annotated
from datetime import datetime, timezone
import time
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    model_validator
)

from api.core.base.responses import BaseResponseData, BaseResponse


class SettingsBase(BaseResponseData):
    """
    SettingsBase
    """

    id: str = Field(examples=["a0c96829-e826-4ab3-90f6-55b6c9a533bb"])
    user_id: str = Field(examples=["a0c96829-e826-4ab3-90s6-55b6c9a533bb"])
    language: Optional[str] = Field(examples=["en"])
    dark_mode: Optional[bool] = Field(examples=[False])
    voice_call: Optional[bool] = Field(examples=[True])
    video_call: Optional[bool] = Field(examples=[True])
    notifications: Optional[bool] = Field(examples=[True])
    anonymous_mode: Optional[bool] = Field(examples=[False])
    travel_mode: Optional[bool] = Field(examples=[False])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])


class SettingsUpdateRequest(BaseModel):
    """
    Schema for settings update request
    """

    language: Annotated[
        Optional[str],
        StringConstraints(
            max_length=5, min_length=2, strip_whitespace=True, strict=True
        ),
    ] = Field(None, examples=["en"])
    dark_mode: Optional[bool] = Field(None, examples=[False])
    voice_call: Optional[bool] = Field(None, examples=[True])
    video_call: Optional[bool] = Field(None, examples=[True])
    notifications: Optional[bool] = Field(None, examples=[True])
    anonymous_mode: Optional[bool] = Field(None, examples=[False])
    travel_mode: Optional[bool] = Field(None, examples=[False])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates fields.
        """
        language: str = values.get("language", "")
        if language not in ["fr", "en", "es"]:
            raise ValueError(f"{language} must be either fr, en, es.")
        return values
        

class SettingsResponse(BaseResponse):
    """
    Setting response model
    """

    data: SettingsBase