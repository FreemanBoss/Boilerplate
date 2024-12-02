import math
from fastapi import Request, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from api.core.base.services import Service

from api.v1.trusted_devices.model import TrustedDevice
from api.v1.auth.dependencies import authenticate_user

from api.v1.trusted_devices.schema import DeviceInfo
from api.v1.trusted_devices.schema import(
    RemoveTrustedDeviceOutput,
    TrustedDeviceBase,
    AllTrustedDeviceOutput
)


class TrustedDeviceService(Service):
    """
    Service class for trusted devices.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

    async def register_trusted_device(
        self,
        user_id: str,
        device_info: DeviceInfo,
        session: AsyncSession
    ):
        """Register a new trusted device."""

        existing_trust = await self.fetch(
                {"user_id": user_id, "device_id": device_info.device_id},
                session
            )
            
        if existing_trust:
            raise HTTPException(
                status_code=400,
                detail="Device is already trusted"
            )
        data = {
            'user_id': user_id,
            'device_id': device_info.device_id,
            'platform': device_info.platform,
            'device_name': device_info.device_name,
            "last_used_at": datetime.now(timezone.utc)
        }

        _ = await self.create(data, session)


    async def verify_device_trust(
        self,
        user_id: str,
        device_info: DeviceInfo,
        session: AsyncSession
    ) -> bool:
        """Check if device is trusted and recently used."""

        filter = {
            "user_id": user_id,
            "device_id": device_info.device_id,
            "is_trusted": True
        }

        trusted_device = await self.fetch(filter, session)

        if trusted_device:
            # Update last used timestamp
            trusted_device.last_used_at = datetime.now(timezone.utc)
            await session.commit()
            
            # Check if device was used recently (within 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            return trusted_device.last_used_at > thirty_days_ago

        return False


    async def remove_trusted_device(
        self,
        request: Request,
        device_id: str,
        session: AsyncSession,
        access_token: str
    ) -> Optional[RemoveTrustedDeviceOutput]:
        """Removes a trusted device

        Args:
            request(object): request object
            device_id(str): id of the device to remove.
            session(asyncsession): database async session object.
            access_token(str): request token.
        Returns:
            RemoveTrustedDeviceOutput(object): contains success or error message
        """

        claims = await authenticate_user(request, access_token)

        device = await self.fetch(
            {"id": device_id, "user_id": claims.get("user_id")},
            session
        )
        
        if device:
            device.is_trusted = False
            await session.commit()
            return RemoveTrustedDeviceOutput(
                message="Device removed from trusted devices"
            )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )


    async def get_trusted_devices(
        self,
        request: Request,
        params: dict,
        session: AsyncSession,
        access_token: str
    ) -> Optional[AllTrustedDeviceOutput]:
        """
        Fetches all trusted devices.

        Args:
            request(object): request object
            session(asyncsession): database async session object.
            access_token(str): request token.
        Returns:
            AllTrustedDeviceOutput(object): contains list of all blocked users
        """

        claims = await authenticate_user(request, access_token)

        where = {"user_id": claims.get("user_id")}

        if params["is_trusted"] is not None:
            where.update({"is_trusted": params["is_trusted"]})

        filterer =  {"sort": "last_used_at"}

        devices = await self.fetch_all(
            filterer=filterer, session=session, where=where
        )

        total_items = len(devices)

        return AllTrustedDeviceOutput(
            message="Trusted devices list successfully generated",
            total_items=total_items,
            data=[
                TrustedDeviceBase.model_validate(device)
                for device in devices
            ]
        )


trusted_device_service = TrustedDeviceService(TrustedDevice)
