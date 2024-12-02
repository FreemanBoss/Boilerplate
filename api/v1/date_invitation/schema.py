from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BookDateForTwoSchema(BaseModel):
    """
    Schema for booking a date for two individuals.
    """
    location_id: str = Field(
        examples=["1234-5678-9876-5432"], description="Unique ID of the location."
    )
    date: datetime = Field(
        examples=["2024-12-25T18:30:00"],
        description="The date and time for the booking."
    )
    partner_name: str = Field(
        examples=["John Doe"], description="The name of the invitee or partner."
    )
    partner_contact: str = Field(
        examples=["+1234567890"],
        description="The contact information of the invitee or partner."
    )


class BookDateForSelfSchema(BaseModel):
    """
    Schema for booking a date for self.
    """
    location_id: str = Field(
        examples=["1234-5678-9876-5432"], description="Unique ID of the location."
    )
    date: datetime = Field(
        examples=["2024-12-25T18:30:00"],
        description="The date and time for the booking."
    )


class BookingSuccessSchema(BaseModel):
    """
    Schema for a successful booking response.
    """
    status_code: int = Field(
        default=201, examples=[201], description="HTTP status code for success."
    )
    message: str = Field(
        default="Booking created successfully.",
        examples=["Booking created successfully."]
    )
    booking_id: Optional[str] = Field(
        examples=["12345-67890-12345"], description="Unique ID for the created booking."
    )


class BookingErrorSchema(BaseModel):
    """
    Schema for an error during booking.
    """
    status_code: int = Field(
        default=400, examples=[400], description="HTTP status code for the error."
    )
    message: str = Field(
        default="Invalid data provided.",
        examples=["Invalid data provided."]
    )
    details: Optional[str] = Field(
        examples=["Location ID is required."],
        description="Detailed explanation of the error."
    )
