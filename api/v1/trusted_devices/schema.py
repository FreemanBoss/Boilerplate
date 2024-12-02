from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, List, Annotated
from datetime import datetime, timezone
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    StringConstraints,
    model_validator
)

import re
import unicodedata
from bleach import clean

from api.core.base.responses import BaseResponse, BaseResponseData

class TrustedDeviceBase(BaseResponseData):
    """
    TrustedDeviceBase
    """

    id: str = Field(examples=["a0c96829-e826-4ab3-90f6-55b6c9a533bb"])
    user_id: str = Field(examples=["a0c96829-e826-4ab3-90s6-55b6c9a533bb"])
    device_id: str = Field(examples=["a0c96829-e826-4ab3-90s6-55b6c9a533bb"])
    platform: str = Field(examples=["Andriod"])
    device_name: str = Field(examples=["Galaxy S8"])
    last_used_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    is_trusted: bool = Field(examples=[True])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])


class DevicePlatform(str, Enum):
    IOS = "ios"
    ANDROID = "android"

class DeviceInfo(BaseModel):
    """Device details"""

    device_id: Annotated[
        str,
        StringConstraints(max_length=64, min_length=3, strip_whitespace=True)
    ] = Field(examples=["akjfokallkd09u0454l5lkaj095"])
    platform: DevicePlatform = Field(examples=["ios"])
    device_name: Annotated[
        str,
        StringConstraints(max_length=32, min_length=3, strip_whitespace=True)
    ] = Field(examples=["Galaxy S8"])
    app_version: Annotated[
        str,
        StringConstraints(max_length=12, min_length=3, strip_whitespace=True)
    ] = Field(examples=["1.0.0"])


    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates all fields
        """
        device_id: str = values.get("device_id", "")
        platform: str = values.get("platform", "")
        device_name: str = values.get("device_name", "")
        app_version: str = values.get("app_version", "")
        
        if platform:
            if platform not in ["ios", "andriod"]:
                raise ValueError("platform must be either ios or andriod")
            validate_fields(platform, "platform")
            values["platform"] = unicodedata.normalize("NFKC", clean(platform)).lower()
    
        if device_name:
            validate_fields(device_name, "device_name")
            values["device_name"] = unicodedata.normalize(
                "NFKC", clean(device_name.lower())
            ).title()

        if device_id:
            validate_fields(device_id, "device_id")
            values["device_id"] = unicodedata.normalize("NFKC", clean(device_id))

        if app_version:
            validate_fields(app_version, "app_version")
            values["app_version"] = unicodedata.normalize("NFKC", clean(app_version))

        return values

class RemoveTrustedDeviceOutput(BaseResponse):
    message: str = Field(examples=["Device removed from trusted devices"])

class AllTrustedDeviceOutput(BaseResponse):
    """All trusted devices schema"""

    message: str = Field(examples=["Successfully fetched all trusted devices"])
    total_items: int = Field(examples=[5])
    data: List[TrustedDeviceBase]


def validate_fields(name: str, field: str) -> None:
    """
    Checks for white space
    """
    # offensive words
    offensive_words = [
        "fuck",
        "ass",
        "pussy",
        "asshole",
        "niggar",
        "bitch",
        "hoe",
        "cum",
        "scum",
        "bastard",
    ]

    offensive_regex = r"\b(?:" + "|".join(offensive_words) + r")\b"
    # check for offfensive words
    if re.search(offensive_regex, name):
        raise ValueError(f"{field} contains offensive language")