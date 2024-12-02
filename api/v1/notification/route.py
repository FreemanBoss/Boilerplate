from typing import Annotated
from fastapi import APIRouter, status, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.notification.schema import (
    GetNotoficationOutputSchema,
    UpdateNotoficationOutputSchema,
    AllNotoficationsSchema,
    UserUpdateNotificationSchema,
)
from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.notification.service import notification_service
from api.v1.auth.dependencies import oauth2_scheme


logger = create_logger("NOTIFICATIONS Route")

notification = APIRouter(prefix="/notifications", tags=["NOTIFICATIONS"])


@notification.put(
    "/{notification_id}",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=UpdateNotoficationOutputSchema,
)
async def update_notification(
    notification_id: str,
    request: Request,
    schema: UserUpdateNotificationSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Marks a notification as read or not read."""
    return await notification_service.update_notification(
        session=session,
        request=request,
        access_token=access_token,
        notification_id=notification_id,
        is_read=schema.is_read,
    )


@notification.get(
    "/{notification_id}",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=GetNotoficationOutputSchema,
)
async def fetch_notification(
    notification_id: str,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Retrieves a notification"""
    return await notification_service.fetch_notification(
        session=session,
        request=request,
        access_token=access_token,
        notification_id=notification_id,
    )


@notification.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AllNotoficationsSchema,
)
async def fetch_notifications(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    page: int = Query(default=1, examples=[1]),
    limit: int = Query(default=10, examples=[10]),
    sort_order: str = Query(default="desc", examples=["desc", "asc"], strict=True),
    sort: str = Query(
        default="created_at", examples=["created_at", "updated_at"], strict=True
    ),
    is_read: bool = Query(default=None, examples=[True]),
):
    """Retrieves notifications."""
    valid_params = {
        "page": page,
        "limit": limit,
        "sort_order": sort_order,
        "sort": sort,
        "is_read": is_read,
    }
    return await notification_service.fetch_notifications(
        params=valid_params,
        session=session,
        request=request,
        access_token=access_token,
    )
