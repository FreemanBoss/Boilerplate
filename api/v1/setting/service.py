from fastapi import Request, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.base.services import Service

from api.v1.setting.model import Setting
from api.v1.auth.dependencies import authenticate_user
from api.v1.setting.schema import SettingsBase, SettingsUpdateRequest, SettingsResponse


class SettingService(Service):
    """
    Service class for profile.
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

    async def fetch_setting(
        self, request: Request, session: AsyncSession, access_token: str
    ) -> Optional[SettingsResponse]:
        """Fetches a users settings

        Args:
            request(object): request object
            session(asyncsession): database async session object.
            access_token(str): request token.
        Returns:
            SettingsResponse(object): contains settings data and success message if successful
        """

        async with session.begin().session as session:

            claims = await authenticate_user(request, access_token)

            settings = await self.fetch({"user_id": claims.get("user_id")}, session)
            print("settings: ", settings)

            if not settings:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found"
                )

            settings_base = SettingsBase.model_validate(settings)

            return SettingsResponse(
                message="Settings successfully fetched.", data=settings_base
            )

    async def update_settings(
        self,
        request: Request,
        schema: SettingsUpdateRequest,
        session: AsyncSession,
        access_token: str,
    ) -> Optional[SettingsResponse]:
        """
        Updates a users settings.

        Args:
            request(object): request object
            schema(object): pydantic model.
            session(asyncsession): database async session object.
            access_token(str): request token.
        Returns:
            SettingsResponse(object): contains settings data and success message if successful
        """

        async with session.begin().session as session:

            claims = await authenticate_user(request, access_token)

            settings = await self.fetch({"user_id": claims.get("user_id")}, session)

            if not settings:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found"
                )

            settings_data = schema.model_dump(exclude_unset=True)

            where = [{"id": settings.id}, settings_data]

            # update the settings
            updated_setting = await self.update(where, session)

            settings_base = SettingsBase.model_validate(updated_setting)

            return SettingsResponse(
                message="Settings successfully updated.", data=settings_base
            )


setting_service = SettingService(Setting)
