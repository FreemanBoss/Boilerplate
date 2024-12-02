"""
pydantic models
"""

import re
import unicodedata
from typing import Optional, Annotated, List, Dict
from datetime import datetime, timezone, date
import time
from pydantic import BaseModel, Field, ConfigDict, StringConstraints, model_validator
from bleach import clean

from api.core.base.responses import BaseResponseData, BaseResponse


class ProfileBase(BaseResponseData):
    """
    ProfileBase
    """

    id: str = Field(examples=["a0c96829-e826-4ab3-90f6-55b6c9a533bb"])
    user_id: str = Field(examples=["a0c96829-e826-4ab3-90s6-55b6c9a533bb"])
    recovery_email: Optional[str] = Field(examples=["johnson@email.com"])
    verified: Optional[bool] = Field(examples=[True])
    phone: Optional[str] = Field(examples=["+00014256747"])
    bio: Optional[str] = Field(examples=["I am the Man!"])
    height: Optional[str] = Field(examples=["178 CM"])
    genotype: Optional[str] = Field(examples=["AA"])
    last_active_at: Optional[str] = Field(examples=[time.asctime()])
    gender: Optional[str] = Field(examples=["Male"])
    date_of_birth: Optional[date] = Field(examples=[date(2024, 9, 4)])
    location: Optional[str] = Field(examples=["Suruler, Lagos, Nigeria."])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])


class ProfileUpdateRequest(BaseModel):
    """
    Schema for profile update request
    """

    first_name: Annotated[
        str,
        StringConstraints(
            max_length=20, min_length=3, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Waas"])
    date_of_birth: date = Field(examples=[date(2024, 9, 4)])
    gender: str = Field(examples=["Male"])
    joining_purpose: str = Field(examples=["Date"])
    preferred_gender: str = Field(examples=["Female"])
    desired_relationship: List[str] = Field(
        examples=[["friendship", "long-term", "casual"]]
    )
    height: Optional[str] = Field(examples=["178 CM"])
    genotype: Optional[str] = Field(examples=["AA"])
    hobbies: Optional[List[str]] = Field(examples=[["Football", "Writing"]])
    ideal_partner_qualities: Optional[List[str]] = Field(
        examples=[["Ambition", "Loyalty"]]
    )
    lifestyle_habits: Optional[List[str]] = Field(examples=[["Drinking", "Smoking"]])
    family_plans: Optional[dict] = Field(examples=[{"has_kids": "Kids"}])
    religion: Optional[str] = Field(examples=["Atheist"])
    political_views: Optional[str] = Field(examples=["Liberal"])
    bio: Annotated[
        Optional[str], StringConstraints(max_length=32, strip_whitespace=True)
    ] = Field(examples=["I love reading..."])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates all fields
        """
        genotype: str = values.get("genotype", "")
        first_name: str = values.get("first_name", "")
        date_of_birth: date = values.get("date_of_birth", None)
        gender: str = values.get("gender", "")
        joining_purpose: str = values.get("joining_purpose", "")
        preferred_gender: str = values.get("preferred_gender", "")
        desired_relationship: List[str] = values.get("desired_relationship", [""])
        hobbies: List[str] = values.get("hobbies", [""])
        lifestyle_habits: List[str] = values.get("lifestyle_habits", [""])
        family_plans: Dict[str, str] = values.get("family_plans", {})

        if gender:
            if gender.lower() not in ["male", "femail"]:
                raise ValueError("Gender Must be male or female")
            values["gender"] = clean(gender.lower())
        if not first_name:
            raise ValueError("First name cannot be empty.")

        if not date_of_birth:
            raise ValueError("date of birth must be provided")

        if not gender:
            raise ValueError("Gender must be provided")

        if not joining_purpose:
            raise ValueError("Please select what brings you here")

        if not preferred_gender:
            raise ValueError("Please select your preferred gender")

        if not desired_relationship:
            raise ValueError("Please select what you hope to find")

        if first_name:
            validate_names(first_name, "first_name")
            values["first_name"] = unicodedata.normalize(
                "NFKC", clean(first_name.lower())
            ).title()
        values["joining_purpose"] = joining_purpose.lower()
        values["preferred_gender"] = preferred_gender.lower()

        if hobbies:
            if not isinstance(hobbies, list):
                raise ValueError("hobbies must be a list of hobbies")
            values["hobbies"] = [
                clean(str(hobby).lower())
                for hobby in hobbies
                if len(str(hobby).strip()) < 35
            ]
        if family_plans:
            if not isinstance(family_plans, dict):
                raise ValueError(
                    "family_plans must be of type json, hashed-map, object, or dictionary"
                )
            values["family_plans"] = {
                key: clean(str(value).lower())
                for key, value in family_plans.items()
                if len(str(value).strip()) < 35
            }
        if genotype and genotype.upper() not in [
            "AA",
            "AS",
            "SS",
            "AC",
            "SC",
        ]:
            raise ValueError("Invalid genotype")
        values["genotype"] = genotype.upper()

        if not isinstance(lifestyle_habits, list):
            raise ValueError("lifestyle_habits must be a list, slice or an array")
        values["lifestyle_habits"] = [
            clean(str(habit).lower())
            for habit in lifestyle_habits
            if len(str(habit).strip()) < 35
        ]

        return values


class ProfileUpdateResponse(BaseResponse):
    """
    Registration client response model
    """

    data: ProfileBase


# ---------------------------------------------------------
# update individual fields


class ProfileUpdateSchema(BaseModel):
    """
    schema for updating individual profile fields
    """

    hobbies: Optional[List[str]] = Field(examples=[["Football", "Writing"]])
    lifestyle_habits: Optional[List[str]] = Field(
        examples=[["yes, i drink", "i smoke sometimes"]]
    )
    family_plans: Optional[dict] = Field(examples=[{"have_kids": "I have Kids"}])
    religion: Annotated[
        Optional[str], StringConstraints(strip_whitespace=True, max_length=35)
    ] = Field(examples=["Atheist"])
    political_view: Annotated[
        Optional[str], StringConstraints(strip_whitespace=True, max_length=35)
    ] = Field(examples=["Liberal"])
    bio: Annotated[
        Annotated[Optional[str], StringConstraints(strip_whitespace=True)],
        StringConstraints(max_length=40, min_length=6, strip_whitespace=True),
    ] = Field(examples=["I love reading..."])
    genotype: Annotated[
        Optional[str], StringConstraints(strip_whitespace=True, max_length=3)
    ] = Field(examples=["AA"])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validates all fields
        """
        hobbies: list = values.get("hobbies", "")
        lifestyle_habits: list = values.get("lifestyle_habits", None)
        family_plans: dict = values.get("family_plans", "")
        religion: str = values.get("religion", "")
        political_view: str = values.get("political_view", "")
        bio: str = values.get("bio", "")
        genotype: str = values.get("genotype", [""])

        if (
            not hobbies
            and not lifestyle_habits
            and not family_plans
            and not religion
            and not political_view
            and not bio
            and not genotype
        ):
            raise ValueError("Must have atleast one field to complete update request.")

        if hobbies:
            if not isinstance(hobbies, list):
                raise ValueError("hobbies must be a list of hobbies")
            values["hobbies"] = [
                clean(str(hobby).lower())
                for hobby in hobbies
                if len(str(hobby).strip()) < 35
            ]

        if lifestyle_habits:
            if not isinstance(lifestyle_habits, list):
                raise ValueError("lifestyle_habits must be a list, slice or an array")
            values["lifestyle_habits"] = [
                clean(str(habit).lower())
                for habit in lifestyle_habits
                if len(str(habit).strip()) < 35
            ]

        if family_plans:
            if not isinstance(family_plans, dict):
                raise ValueError(
                    "family_plans must be of type json, hashed-map, object, or dictionary"
                )
            values["family_plans"] = {
                key: clean(str(value).lower())
                for key, value in family_plans.items()
                if len(str(value).strip()) < 35
            }

        if religion:
            if not isinstance(religion, str):
                raise ValueError("religion must be a list of type string")
            values["religion"] = clean(str(religion.lower()))

        if political_view:
            if not isinstance(political_view, str):
                raise ValueError("political_view must be  of type string")
            values["political_view"] = clean(str(political_view.lower()))

        if bio:
            if not isinstance(bio, str):
                raise ValueError("bio must be  of type string")
            values["bio"] = clean(str(bio))

        if genotype:
            if not isinstance(genotype, str):
                raise ValueError("genotype must be of type string")
            values["genotype"] = clean(str(genotype))
            if genotype and genotype.upper() not in [
                "AA",
                "AS",
                "SS",
                "AC",
                "SC",
            ]:
                raise ValueError("Invalid genotype")

        return values


class UpdateProfileBase(ProfileBase):
    """
    Update profile base
    """

    location: Optional[dict] = Field(
        examples=[{"city": "Kano", "state": "Kano", "country": "Nigeria"}]
    )
    genotype: Optional[str] = Field(examples=["AA"])
    joining_purpose: Optional[str] = Field(examples=["passion"])
    preferred_gender: Optional[str] = Field(examples=["female"])
    desired_relationship: Optional[list] = Field(examples=["date"])
    ideal_partner_qualities: Optional[list] = Field(examples=["smart"])
    location_preference: Optional[str] = Field(examples=["Heaven"])
    age_range: Optional[str] = Field(examples=["24 to 27"])
    distance_range: Optional[str] = Field(examples=["1000km"])
    hobbies: Optional[list] = Field(examples=["reading"])
    lifestyle_habits: Optional[list] = Field(examples=[["don't smoke"]])
    family_plans: Optional[dict] = Field(examples=[{"want_kids": "want plenty kids"}])
    religion: Optional[str] = Field(examples=["christain"])
    political_view: Optional[str] = Field(examples=["AA"])
    bio: Optional[str] = Field(examples=["AA"])
    genotype: Optional[List[str]] = Field(examples=["AA"])


class UpdateResponseSchema(BaseModel):
    """
    Profile response.
    """

    status_code: int = Field(examples=[200], default=200)
    message: str = Field(
        examples=["Profile Updated successfully."],
        default="Profile Updated successfully.",
    )
    data: UpdateProfileBase


# -----------------------------------------------------------
# get profile
class FetchProfileResponseSchema(BaseModel):
    """
    Fetch profile response schema.
    """

    status_code: int = Field(examples=[200], default=200)
    message: str = Field(
        examples=["Profile retrieved successfully."],
        default="Profile retrieved successfully.",
    )
    data: UpdateProfileBase


class DeleteUserResponse(BaseResponse):
    """
    Delete user endpoint response model
    """

    message: Optional[str] = Field(
        examples=["User successfully deleted"], default="User successfully deleted"
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
