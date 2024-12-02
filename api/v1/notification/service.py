from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException

from api.core.base.services import Service
from api.v1.notification.model import Notification, PushNotification
from api.v1.notification.schema import (
    GetNotoficationOutputSchema,
    AllNotoficationsSchema,
    NotificationBase,
    UpdateNotoficationOutputSchema,
)
from api.v1.auth.dependencies import verify_token
from api.utils.validate_pagination import validate_pagination

MAX_RETRIES = 3


class NotificationService(Service):
    """
    Service class for Notification resource.
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

    async def update_notification(
        self,
        is_read: bool,
        session: AsyncSession,
        request: Request,
        access_token: str,
        notification_id: str,
    ) -> Optional[UpdateNotoficationOutputSchema]:
        """
        sets  a notification to read or not read.

        Args:
            is_read(bool): the status to update for the notification
            session(AsyncSession): database session object.
            request(Request): request object.
            access_token(str): the acess_token from headers.
            notification_id(str): the id of the notification to update.
        Returns:
            NotoficationOutputSchema(object): updated notification.
        Raises:
            HttpException.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )

        notification_to_update = await self.fetch({"id": notification_id}, session)
        if not notification_to_update:
            raise HTTPException(status_code=400, detail="Notification not found.")
        updated_notification = await self.update(
            [
                {"id": notification_id, "user_id": claims.get("user_id")},
                {"is_read": is_read},
            ],
            session,
        )

        notification_base = NotificationBase.model_validate(
            updated_notification, from_attributes=True
        )

        return UpdateNotoficationOutputSchema(data=notification_base)

    async def fetch_notifications(
        self,
        params: dict,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[AllNotoficationsSchema]:
        """
        Retrieves a notification.

        Args:
            params(dict): the pagination.
            session(AsyncSession): database session object.
            request(Request): request object.
            access_token(str): the acess_token from headers.
        Returns:
            AllNotoficationsSchema(object): retrieved notifications.
        Raises:
            HttpException.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )

        where = {"user_id": claims.get("user_id")}
        if params["is_read"]:
            where.update({"is_read": params["is_read"]})

        filterrer = await validate_pagination(params)

        notifications = await self.fetch_all(
            filterer=filterrer, session=session, where=where
        )

        return AllNotoficationsSchema(
            data=[
                NotificationBase.model_validate(notification, from_attributes=True)
                for notification in notifications
            ]
        )

    async def fetch_notification(
        self,
        notification_id: str,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[GetNotoficationOutputSchema]:
        """
        Retrieves a notification.

        Args:
            notification_id(str): the id of the notification.
            session(AsyncSession): database session object.
            request(Request): request object.
            access_token(str): the acess_token from headers.
        Returns:
            NotoficationOutputSchema(object): retrieved notification.
        Raises:
            HttpException.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )

        notification = await self.fetch(
            session=session,
            filterer={"id": notification_id, "user_id": claims.get("user_id")},
        )
        if not notification:
            raise HTTPException(status_code=400, detail="Notification not found")

        return GetNotoficationOutputSchema(
            data=NotificationBase.model_validate(notification, from_attributes=True)
        )


class PushNotificationService(Service):
    """
    Service class for PushNotification resource.
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


notification_service = NotificationService(Notification)
push_notification_service = PushNotificationService(PushNotification)
