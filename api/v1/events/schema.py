""" event schemas file"""
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EventBase(BaseModel):
    """
    Base schema for event details.
    """
    id: str = Field(examples=["abcd-1234-efgh-5678"])
    name: str = Field(examples=["Music Festival"])
    details: Optional[str] = Field(examples=["An amazing festival with top artists."])
    date: datetime = Field(examples=[datetime.now()])
    location: str = Field(examples=["Central Park, New York"])
    ticket_price: float = Field(examples=[50.00], description="Price per ticket")
    banner: Optional[Dict[str, str]] = Field(
        examples=[{"banner_1": "https://aws.com/photos/banner/music_festival.png"}]
    )
    tickets_available: int = Field(examples=[500])
    total_capacity: int = Field(examples=[1000])
    ticket_types: str = Field(default="regular", examples=["regular", "vip"])

    model_config = ConfigDict(from_attributes=True)


class EventTicketBase(BaseModel):
    """
    Base schema for event tickets.
    """
    id: str = Field(examples=["ticket-1234-5678-91011"])
    user_id: str = Field(examples=["user-1234"])
    event_id: str = Field(examples=["abcd-1234-efgh-5678"])
    payment_id: Optional[str] = Field(examples=["pay-9876"])
    status: str = Field(default="reserved", examples=["reserved", "paid"])
    ticket_price: float = Field(examples=[50.00])
    quantity: int = Field(default=1, examples=[1])
    ticket_type: str = Field(default="regular", examples=["regular", "vip"])

    model_config = ConfigDict(from_attributes=True)




class AllEventsOutSchema(BaseModel):
    """
    Schema for listing all events within a location or based on user preferences.
    """
    status_code: int = Field(default=200, examples=[200])
    page: int
    limit: int
    total_pages: int
    total_items: int
    message: str = Field(
        default="Events Retrieved Successfully.",
        examples=["Events Retrieved Successfully."]
    )
    data: List[EventBase]


class SearchEventsOutSchema(BaseModel):
    """
    Schema for retrieving events that match a search term within a user location.
    """
    status_code: int = Field(default=200, examples=[200])
    page: int
    limit: int
    total_pages: int
    total_items: int
    message: str = Field(
        default="Matching Events Retrieved Successfully.",
        examples=["Matching Events Retrieved Successfully."]
    )
    data: List[EventBase]



class FetchEventDetailSchema(BaseModel):
    """
    Schema for fetching details of a specific event, including attendees.
    """
    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Event Retrieved Successfully.",
        examples=["Event Retrieved Successfully."]
    )
    data: EventBase
    attendees: Optional[List[str]] = Field(
        default=[],
        examples=[["user-1234", "user-5678"]],
        description="List of user IDs who purchased tickets for the event."
    )


class BookEventTicketSchema(BaseModel):
    """
    Schema for booking an event ticket.
    """
    event_id: str = Field(examples=["abcd-1234-efgh-5678"])
    quantity: int = Field(default=1, examples=[1])
    ticket_type: str = Field(default="regular", examples=["regular", "vip"])

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "abcd-1234-efgh-5678",
                "quantity": 2,
                "ticket_type": "vip"
            }
        }


class BookEventTicketResponseSchema(BaseModel):
    """
    Schema for response after booking an event ticket.
    """
    status_code: int = Field(default=201, examples=[201])
    message: str = Field(
        default="Ticket booked successfully. Awaiting payment.",
        examples=["Ticket booked successfully. Awaiting payment."]
    )
    data: EventTicketBase


class FetchEventTicketSchema(BaseModel):
    """
    Schema for fetching details of a purchased event ticket.
    """
    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Ticket Retrieved Successfully.",
        examples=["Ticket Retrieved Successfully."]
    )
    data: EventTicketBase
