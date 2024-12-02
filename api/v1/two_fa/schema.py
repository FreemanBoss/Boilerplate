"""
pydantic models
"""

from enum import Enum
from typing import Optional, Annotated, List
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    model_validator
)

from api.core.base.responses import BaseResponse
from api.v1.trusted_devices.schema import DeviceInfo


class TwoFactorVerifySchema(BaseModel):
    """
    Vefification code from authenticator schema
    """

    code: Annotated[
        str,
        StringConstraints(
            max_length=6, min_length=6, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["898000"])
    
class TwoFactorLoginVerifySchema(BaseModel):
    """2FA login schema"""

    temp_token: str = Field(examples=["ejyjeakjldfjlkjdlk..."])
    code: Annotated[
        str,
        StringConstraints(
            max_length=6, min_length=6, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["898000"])
    device_info: DeviceInfo

class TwoFactorStatusSchema(BaseModel):
    is_enabled: bool
    created_at: Optional[datetime]

    
class TwoFactorSetupSchema(BaseModel):
    """2FA setup request schema"""

    password: str = Field(examples=["lajkkdljfa"])
    password: Annotated[
        str,
        StringConstraints(
            max_length=30, min_length=12, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Johnson1234@"])
    device_info: DeviceInfo

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates all fields
        """
        password: str = values.get("password", "")

        if not password:
            raise ValueError("Password is required.")

        validate_password(password)

        return values


class TwoFactorMethod(str, Enum):
    TOTP = "totp"
    PUSH = "push"  # For future push notification implementation


class TwoFactorSetupOutputData(BaseModel):
    """
    2FA setup response data
    """

    secret_key: str
    auth_uri: str  # For deep linking into authenticator apps
    backup_codes: List[str]
    setup_method: TwoFactorMethod


class TwoFactorSetupOutputSchema(BaseResponse):
    """
    2FA setup response schema
    """

    data: TwoFactorSetupOutputData


class TwoFactorVerifyOutputSchema(BaseResponse):
    """
    2FA setup verification response schema
    """

    data: List[str]


def validate_password(password: str) -> None:
    """
    Validates password.
    """
    # allowed special characters for password
    password_allowed = "!@#&-_,."
    not_allowed = "+="  # Original not_allowed string

    # Adding all special characters
    special_chars = r'"$%\'()*+,./:;<=>?[\\]^`{|}~'
    not_allowed += special_chars

    if not any(char for char in password if char.islower()):
        raise ValueError(f"{password} must contain at least one lowercase letter")
    if not any(char for char in password if char.isupper()):
        raise ValueError(f"{password} must contain at least one uppercase letter")
    if not any(char for char in password if char.isdigit()):
        raise ValueError(f"{password} must contain at least one digit character")
    if not any(char for char in password if char in password_allowed):
        raise ValueError(
            f"{password} must contain at least one of these special characters {password_allowed}"
        )
    if any(char for char in password if char == " "):
        raise ValueError(f"{password} cannot contain a white space character")
    if any(char in not_allowed for char in password):
        raise ValueError(
            f"contains invalid characters. Allowed special characters: {password_allowed}"
        )