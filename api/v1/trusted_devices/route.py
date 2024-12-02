from typing import Annotated, Optional
from fastapi import APIRouter, status, Request, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession


from api.v1.trusted_devices.schema import (
    AllTrustedDeviceOutput, RemoveTrustedDeviceOutput
)
from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.auth.dependencies import oauth2_scheme


from api.database.database import get_async_session
from api.v1.trusted_devices.service import trusted_device_service


trusted_devices = APIRouter(prefix="/trusted-devices", tags=["AUTHENTICATION"])

@trusted_devices.get(
    "",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=AllTrustedDeviceOutput
)
async def list_trusted_devices(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    is_trusted: Annotated[bool, Query(examples=[True])] = None
) -> AllTrustedDeviceOutput:
    """List all trusted devices for the user

    Args:
        request(object): request object
        session(asyncsession): database async session object.
        access_token(str): request token.
        is_trusted(bool): query parameter
    Returns:
        AllTrustedDeviceOutput(object): contains success or error message
    """

    valid_params = {
        "is_trusted": is_trusted
    }

    return await trusted_device_service.get_trusted_devices(
        request,
        valid_params,
        session,
        access_token
    )


@trusted_devices.delete(
    "/{device_id}",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=RemoveTrustedDeviceOutput
)
async def remove_trusted_device(
    request: Request,
    device_id: Annotated[str, Path(description="String identifier derived from the request URL")],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)]
)-> Optional[RemoveTrustedDeviceOutput]:
    """Removes a trusted device.

    Args:
        request(object): request object
        device_id(str): id of the device to remove.
        session(asyncsession): database async session object.
        access_token(str): request token.
    Returns:
        RemoveTrustedDeviceOutput(object): contains success or error message
    """
   
    return await trusted_device_service.remove_trusted_device(
        request,
        device_id,
        session,
        access_token
    )