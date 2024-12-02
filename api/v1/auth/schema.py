"""
pydantic models
"""

import unicodedata
import dns.resolver
import re
from typing import Annotated, Optional, Union, Dict
from pydantic import (
    BaseModel,
    model_validator,
    StringConstraints,
    EmailStr,
    Field,
)
from email_validator import validate_email, EmailNotValidError
from bleach import clean

from api.v1.user.schema import UserBase
from api.v1.profile.schema import ProfileBase
from api.utils.settings import Config
from api.v1.trusted_devices.schema import DeviceInfo


TESTING = Config.TEST
TEST: bool | None = None

if TESTING:
    TEST = True
else:
    TEST = False


class UserCreate(BaseModel):
    """
    Create user schema.
    """

    email: EmailStr = Field(examples=["habeeb@email.com"])
    password: Annotated[
        str, StringConstraints(min_length=8, max_length=64, strip_whitespace=True)
    ]
    confirm_password: Annotated[
        str, StringConstraints(min_length=8, max_length=64, strip_whitespace=True)
    ] = Field(examples=["Habeeb1234@"])

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates fields
        """
        password, email = values.get("password"), values.get("email")
        confirm_password = values.get("confirm_password")

        validate_password(password)
        if password != confirm_password:
            raise ValueError("Passwords must match")

        if not email:
            raise ValueError("email must be provided")

        values["email"] = validate_user_email(email)

        return values

def validate_mx_record(domain: str):
    """
    Validate mx records for email
    """
    try:
        # Try to resolve the MX record for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        print('mx_records: ', mx_records.response)
        return True if mx_records else False
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False


class RequestEmail(BaseModel):
    """schems for password reset"""

    email: EmailStr = Field(examples=["habeeb@email.com"])

    @model_validator(mode='before')
    @classmethod
    def validate_email(cls, values: dict):
        """
        Validate email
        """
        email = values.get("email")
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        return values


class ResetPasswordResponse(BaseModel):
    """
    Rsponse for reset password
    """
    message: str
    status_code: int

class ResetPasswordSuccesful(BaseModel):
    """
    Rsponse for reset password
    """
    message: str
    status_code: int
    access_token: str
    data: Dict[str, Union[UserBase]]

    @model_validator(mode='before')
    @classmethod
    def check_data_keys(cls, values: dict):
        """
        Validates data
        """
        data = values.get("data", {})
        if "user" not in data:
            raise ValueError("Data must contain 'user'")
        return values


class ResetPasswordRequest(BaseModel):
    reset_token: Annotated[
        str,
        StringConstraints(
            min_length=31
        )
    ]
    new_password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]
    confirm_password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]

    
    @model_validator(mode="before")
    @classmethod
    def password_validator(cls, values: dict):
        """
        Validate passwords
        """
        new_password: str = values.get("new_password")
        confirm_password: str = values.get("confirm_password")
       
        if new_password != confirm_password:
            raise ValueError("new password and confirm password must match")


        if new_password and new_password.strip():
            if not any(c.islower() for c in new_password):
                raise ValueError("Password must have at least one lowercase letter")
            if not any(c.isupper() for c in new_password):
                raise ValueError("Password must have at least one uppercase letter")
            if not any(c.isdigit() for c in new_password):
                raise ValueError("Password must have at least one digit")
            special_characters = "!@#$%&*()-_=:.?"
            if not any(c in special_characters for c in new_password):
                raise ValueError("Password must have at least one special character")
            if ' ' in new_password:
                raise ValueError("Password must not contain white space character")
        return values


class ResendVerificationSchema(BaseModel):
    """
    Schema for resending verification links.
    """

    email: EmailStr = Field(examples=["johnson@email.com"])


class ResendVerificationOutputSchema(BaseModel):
    """
    Schema for resending verification links.
    """

    status_code: int = Field(examples=[200], default=200)
    message: str = Field(
        default="Notification sent successfully.",
        examples=["Notification sent successfully."],
    )
    data: dict = Field(default={}, examples=[{}])


class EmailVerificationOutputSchema(BaseModel):
    """
    Schema for email verification.
    """

    status_code: int = Field(examples=[200], default=200)
    message: str = Field(
        default="Account successfully verified.",
        examples=["Account successfully verified."],
    )
    data: dict = Field(default={}, examples=[{}])


class LoginShema(BaseModel):
    """
    Login schema model.
    """

    email: EmailStr = Field(examples=["Johnson@email.com"])
    password: Annotated[
        str,
        StringConstraints(strict=True, strip_whitespace=True, min_length=6),
    ] = Field(examples=["Habeeb1234@"])
    device_info: DeviceInfo

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates fields.
        """
        email = values.get("email")
        password = values.get("password")

        if not password:
            raise ValueError("password must be provided.")

        validate_user_email(email)
        return values


class AccessToken(BaseModel):
    """
    Access token schems
    """

    access_token: str


class UserLoginSchema(BaseModel):
    """
    User data, profile data, and tokens
    """

    user: UserBase
    profile: ProfileBase
    access_token: str
    refresh_token: str


class LoginOutputSchema(BaseModel):
    """
    Schema for loggin in response
    """

    status_code: int = Field(examples=[200], default=200)
    requires_2fa: bool = Field(
        examples=[False],
        default=False
    )
    message: str = Field(
        default="Login Successful",
        examples=["Login Successful"],
    )
    temp_token: Optional[str] = Field(
        None,
        examples=["some_random_token"]
    )
    data: UserLoginSchema = None



class UserProfileSchema(BaseModel):
    """
    User data and profile data
    """

    user: UserBase
    profile: ProfileBase


class RegisterOutputSchema(BaseModel):
    """
    Registration client response model
    """

    status_code: int = Field(examples=[201], default=201)
    message: str = Field(
        default="User Registered Successfully",
        examples=["User Registered Successfully"],
    )
    data: UserProfileSchema


class RegisterSuperadminSchema(BaseModel):
    """
    Register superadmin schema
    """

    email: Annotated[
        str, StringConstraints(min_length=11, strip_whitespace=True, strict=True)
    ] = Field(examples=["Johnson@example.com"])
    first_name: Annotated[
        str,
        StringConstraints(
            max_length=20, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Johnson"])
    last_name: Annotated[
        str,
        StringConstraints(
            max_length=20, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Doe"])
    password: Annotated[
        str,
        StringConstraints(
            max_length=30, min_length=12, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Johnson1234@"])
    confirm_password: Annotated[
        str,
        StringConstraints(
            max_length=30, min_length=12, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Johnson1234@"])

    secret_token: Annotated[
        str,
        StringConstraints(
            max_length=199, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(
        examples=["dij9048208293dj230imi3iquv3rnvunq3puivnirquvnuivpqi"],
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates all fields
        """
        password: str = values.get("password", "")
        confirm_password = values.get("confirm_password", "")
        email: EmailStr = values.get("email", "")
        first_name: str = values.get("first_name", "")
        last_name: str = values.get("last_name", "")
        secret_token: str = values.get("secret_token", "")

        if not secret_token:
            raise ValueError("secret_token cannot be empty.")

        if not email:
            raise ValueError("email must be provided")

        if password != confirm_password:
            raise ValueError("Passwords must match")

        validate_password(password)

        validate_names(first_name, "first_name")
        validate_names(last_name, "last_name")

        values["first_name"] = unicodedata.normalize(
            "NFKC", clean(first_name.lower())
        ).title()
        values["last_name"] = unicodedata.normalize(
            "NFKC", clean(last_name.lower())
        ).title()

        values["email"] = validate_user_email(email)

        return values


class RegisterStaffSchema(BaseModel):
    """
    Register staff schema
    """

    email: Annotated[
        str, StringConstraints(min_length=11, strip_whitespace=True, strict=True)
    ] = Field(examples=["Johnson@example.com"])
    first_name: Annotated[
        Optional[str],
        StringConstraints(
            max_length=20, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Johnson"], default=None)
    last_name: Annotated[
        Optional[str],
        StringConstraints(
            max_length=20, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Doe"], default=None)
    password: Annotated[
        str,
        StringConstraints(
            max_length=30, min_length=10, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Johnson1234@"])
    confirm_password: Annotated[
        str,
        StringConstraints(
            max_length=30, min_length=10, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Johnson1234@"])

    role: Annotated[
        str,
        StringConstraints(
            max_length=64, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(
        default=None,
        examples=["content-creator"],
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates all fields
        """
        password: str = values.get("password", "")
        confirm_password = values.get("confirm_password", "")
        email: EmailStr = values.get("email", "")
        first_name: str = values.get("first_name", "")
        last_name: str = values.get("last_name", "")
        role: str = values.get("role", "")

        if not role:
            raise ValueError("role cannot be empty.")

        if not email:
            raise ValueError("email must be provided")

        if password != confirm_password:
            raise ValueError("Passwords must match")

        validate_password(password)

        if first_name:
            validate_names(first_name, "first_name")
            values["first_name"] = unicodedata.normalize(
                "NFKC", clean(first_name.lower())
            ).title()

        if last_name:
            validate_names(last_name, "last_name")
            values["last_name"] = unicodedata.normalize(
                "NFKC", clean(last_name.lower())
            ).title()

        values["email"] = validate_user_email(email)

        return values


def validate_user_email(email: str) -> Optional[str]:
    """
    Validates email.
    """
    if not email:
        raise ValueError("email must be provided.")
    if "@" not in email:
        raise ValueError("invalid email address.")
    # emails liable to fraud
    blacklisted_domains = ["example.com", "mailinator.com", "tempmail.com"]
    email_domain = email.split("@")[1].lower()
    if email_domain in blacklisted_domains:
        raise ValueError(f"{email_domain} is not allowed for registration")
    try:
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        pattern = re.compile(email_regex)
        email = validate_email(
            email, check_deliverability=True, test_environment=TEST
        ).normalized
        if not pattern.match(email):
            raise ValueError(f"{email} is invalid")
        return email
    except EmailNotValidError as exc:
        raise ValueError(str(exc))


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


def validate_names(name: str, field: str) -> None:
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
    # not allowed characters for first_name, and last_name
    name_disallowed_char = '1234567890!@~`#$%^&*()_+=-,.<>/?"\\|'

    for c in name:
        if c == " ":
            raise ValueError(f"use of white space is not allowed in {field}")
        if c in name_disallowed_char:
            raise ValueError(f"{c} is not allowed in {field}")

    offensive_regex = r"\b(?:" + "|".join(offensive_words) + r")\b"
    # check for offfensive words
    if re.search(offensive_regex, name):
        raise ValueError(f"{field} contains offensive language")
