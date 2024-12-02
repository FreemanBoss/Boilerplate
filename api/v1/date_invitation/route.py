from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from api.database.database import get_async_session
from api.v1.auth.dependencies import oauth2_scheme, verify_token
from api.v1.date_invitation.schema import (
    BookDateForSelfSchema,
    BookDateForTwoSchema,
    BookingSuccessSchema,
    BookingErrorSchema,
)
from api.v1.place.service import place_service
from api.v1.date_invitation.service import date_booking_service
from typing import Annotated

date = APIRouter(prefix="/places", tags=["PLACES"])

@date.post(
    "/book-date",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingSuccessSchema,
    responses={400: {"model": BookingErrorSchema}},
)
async def book_date_for_self(
    booking_data: BookDateForSelfSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Books a date for a single individual."""
    try:
        
        booking = await date_booking_service.book_for_self(
            user_id=access_token,
            place_id=booking_data.place_id,
            session=session
        )
        return {"status_code": 201,
                "message": "Booking created successfully.",
                "booking_id": booking.id
                }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@date.post(
    "/book-date/for-two",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingSuccessSchema,
    responses={400: {"model": BookingErrorSchema}},
)
async def book_date_for_two(
    booking_data: BookDateForTwoSchema,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Books a date for two individuals."""
    decoded = await verify_token(access_token, request, "access")
    user_id_1 = decoded.get("user_id")
    try:
        
        booking_1, booking_2 = await date_booking_service.book_for_two(
            user_id_1=user_id_1,
            user_id_2=booking_data.partner_user_id,
            place_id=booking_data.place_id,
            session=session
        )
        return {"status_code": 201,
                "message": "Booking created successfully.",
                "booking_id": booking_1.id
                }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@date.post(
    "/cancel-date",
    status_code=status.HTTP_200_OK,
    response_model=BookingSuccessSchema,
    responses={404: {"model": BookingErrorSchema}},
)
async def cancel_date(
    booking_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Cancels a date."""
    try:
        success = await date_booking_service.cancel_date(booking_id=booking_id, session=session)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        return {"status_code": 200, "message": "Booking canceled successfully."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@date.put(
    "/book-date",
    status_code=status.HTTP_200_OK,
    response_model=BookingSuccessSchema,
    responses={400: {"model": BookingErrorSchema}},
)
async def edit_booking(
    booking_id: str,
    new_user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Edits an existing booking."""
    try:
        updated_booking = await date_booking_service.edit_booking(
            booking_id=booking_id, new_user_id=new_user_id, session=session
        )
        return {
            "status_code": 200,
            "message": "Booking updated successfully.",
            "booking_id": updated_booking.id
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
