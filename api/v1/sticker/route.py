from typing import Annotated, Optional
from fastapi import APIRouter, status, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.dependencies import (
    get_async_session,
    oauth2_scheme,
)
from api.v1.sticker.service import sticker_service
from api.v1.sticker.schema import StickerOutSchema, UserStickerOutSchema
from api.utils.responses_schema import responses

sticker = APIRouter(prefix="/stickers", tags=["STICKERS"])


@sticker.get(
    "/{sticker_id}",
    status_code=status.HTTP_200_OK,
    response_model=StickerOutSchema,
    responses=responses,
)
async def retrieve_sticker(
    sticker_id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    request: Request,
):
    """
    Retrieves a single sticker.
    """
    return await sticker_service.retrieve_sticker(
        sticker_id=sticker_id, session=session, token=token, request=request
    )


@sticker.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserStickerOutSchema,
    responses=responses,
)
async def retrieve_all_user_stickers(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    request: Request,
    sent: Optional[bool] = Query(default=None, examples=[True]),
    received: Optional[bool] = Query(default=None, examples=[True]),
):
    """
    Retrieves all  stickers a user has received or sent.
    """
    params = {"sent": sent, "received": received}
    return await sticker_service.retrieve_user_stickers(
        session=session,
        token=token,
        request=request,
        params=params,
    )
