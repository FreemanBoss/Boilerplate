"""
pydantic models
"""

import unicodedata
import re
from typing import Annotated, List
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    model_validator,
    StringConstraints,
    Field,
    ConfigDict,
)
from bleach import clean


class UpdateNotificationSchema(BaseModel):
    """
    Schema for notifications update.
    """

    message: Annotated[
        str, StringConstraints(min_length=11, max_length=80, strip_whitespace=True)
    ] = Field(examples=["Welcome back to our amazing platform, we missed you."])
    title: Annotated[
        str, StringConstraints(min_length=3, max_length=30, strip_whitespace=True)
    ] = Field(examples=["Welcome Back!"])
    notification_type: Annotated[
        str, StringConstraints(min_length=1, max_length=20, strip_whitespace=True)
    ] = Field(examples=["alert", "message", "reminder"])
    status: Annotated[
        str, StringConstraints(min_length=1, max_length=10, strip_whitespace=True)
    ] = Field(examples=["delivered", "pending", "sent"])

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict):
        """
        Validate fields
        """
        message = values.get("message", "")
        title = values.get("title", "")
        notification_type = values.get("notification_type", "")
        status = values.get("status", "")

        if message:
            validate_fields(message, "message")
            values["message"] = unicodedata.normalize("NFKC", clean(message))

        if title:
            validate_fields(title, "title")
            values["title"] = unicodedata.normalize("NFKC", clean(title)).title()

        if notification_type:
            if notification_type not in ["message", "alert", "reminder"]:
                raise ValueError(
                    "notification_type must be either message, alert or reminder"
                )
            validate_fields(notification_type, "notification_type")
            values["notification_type"] = unicodedata.normalize(
                "NFKC", clean(notification_type)
            ).lower()

        if status:
            if status not in ["sent", "pending", "failed"]:
                raise ValueError("status must be either sent, pending or failed")
            validate_fields(status, "status")
            values["status"] = unicodedata.normalize("NFKC", clean(status)).lower()

        if not status and not notification_type and not title and not message:
            raise ValueError("Must provide atleast one valid field to update.")

        return values


class NotificationBase(BaseModel):
    """
    Schema for notification base.
    """

    id: str = Field(examples=["01930617-6d66-746f-8b76-510c11c02149"])
    user_id: str = Field(examples=["01930617-6d66-746f-8b76-510c11c03339"])
    message: str = Field(examples=["Welcome back online, we missed you!"])
    title: str = Field(examples=["welcome back!"])
    notification_type: str = Field(examples=["message"])
    status: str = Field(examples=["delivered"])
    is_read: bool = Field(examples=[True])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)


class AllNotoficationsSchema(BaseModel):
    """
    AllNotoficationsSchema Schema
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Notifications Fetched Successfully.",
        examples=["Notifications Fetched Successfully."],
    )

    data: List[NotificationBase]


class UpdateNotoficationOutputSchema(BaseModel):
    """
    Schema response for updating nitifcation
    """

    status_code: int = Field(default=201, examples=[201])
    message: str = Field(
        default="Notification Updated Successfully.",
        examples=["Notification Updated Successfully."],
    )
    data: NotificationBase


class GetNotoficationOutputSchema(AllNotoficationsSchema):
    """
    Schema response for fetching nitifcation
    """

    message: str = Field(
        default="Notification Retrieved Successfully.",
        examples=["Notification Retrieved Successfully."],
    )
    data: NotificationBase


class UserUpdateNotificationSchema(BaseModel):
    """
    Schema for notifications update.
    """

    is_read: bool = Field(examples=[True])


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
