"""
Stickers module
"""

from typing import Optional
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.core.base.services import Service
from api.v1.auth.dependencies import verify_token, User
from api.v1.sticker.schema import (
    StickerBase,
    StickerOutSchema,
    UserStickerOutSchema,
    ExchangedStickerBase,
)
from api.core.base.services import Service
from api.v1.sticker.model import (
    ExchangedSticker,
    Sticker,
)


class StickerService(Service):
    """
    Service class for sticker.
    """

    def __init__(self, model) -> None:
        super().__init__(model)

    async def receive_sticker(
        self,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ):
        """
        Receives a sticker and populates the user wallet with the sticker value.

        Args:
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode
        Returns:
        """
        pass

    async def retrieve_user_stickers(
        self, session: AsyncSession, request: Request, token: str, params: dict
    ) -> Optional[UserStickerOutSchema]:
        """
        Retreives all sticker a user has received.

        Args:
            session(AsynSession): database async session object.
            request(Request): request object.
            token(str): token to decode.
            params(dict): The query params for received or sent
        Returns:
            UserStickerOutSchema(pydatinc): payload response
        """
        claims = await verify_token(token=token, request=request, token_type="access")
        if params["sent"] and params["received"]:
            raise RequestValidationError(
                errors=["can not have sent=true and received=true at the same time."]
            )
        my_stickers = None

        if not params["sent"] and not params["received"]:
            message = "All Available Stickers retrieved successfully."
            my_stickers = True
            available_stickers = await self.fetch_all(
                filterer={}, session=session, where={}
            )
            all_stickers = [
                ExchangedStickerBase(
                    name=stick.name,
                    id=stick.id,
                    url=stick.url,
                    price=stick.price,
                    total_quantity=0,
                )
                for stick in available_stickers
            ]

        if not my_stickers:
            stmt = select(
                Sticker.id,
                Sticker.price,
                Sticker.name,
                Sticker.url,
                func.sum(ExchangedSticker.quantity).label("total_quantity"),
            ).join(ExchangedSticker, ExchangedSticker.sticker_id == Sticker.id)
        if params["received"]:
            message = "Received stickers retrieved successfully."
            stmt = stmt.where(
                ExchangedSticker.receiver_id == claims.get("user_id")
            ).group_by(Sticker.id)

            result = await session.execute(stmt)
            my_stickers = result.all()
        if params["sent"]:
            message = "Sent stickers retrieved successfully."
            stmt = stmt.where(
                ExchangedSticker.sender_id == claims.get("user_id")
            ).group_by(Sticker.id)

            result = await session.execute(stmt)
            my_stickers = result.all()

        if not my_stickers:
            message = "No Stickers could be found in your Sticker-Chest at the moment."
            return UserStickerOutSchema(message=message, data=[])
        if params["sent"] or params["received"]:
            all_stickers = [
                ExchangedStickerBase(
                    id=stick[0],
                    price=stick[1],
                    name=stick[2],
                    url=stick[3],
                    total_quantity=stick[4],
                )
                for stick in my_stickers
            ]
        return UserStickerOutSchema(message=message, data=all_stickers)

    async def retrieve_sticker(
        self,
        session: AsyncSession,
        request: Request,
        token: str,
        sticker_id: str,
    ) -> Optional[StickerOutSchema]:
        """
        Retrieves a specific sticker a user for view or purchase.

        Args:
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode.
            sticker_id(str): The sticker to retrieve.
        Returns:
            StickerOutSchema(pydantic): payload response.
        """
        claims = await verify_token(token=token, request=request, token_type="access")

        sticker = await self.fetch({"id": sticker_id}, session)
        if not sticker:
            raise HTTPException(status_code=400, detail="sticker not found")

        sticker_base = StickerBase.model_validate(sticker, from_attributes=True)

        return StickerOutSchema(data=sticker_base)

    async def purchase_sticker(
        self,
        payload: dict,
        session: AsyncSession,
        current_user: User,
    ):
        """
        Prepares a purchase for a sticker.

        Args:
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode
        Returns:
        """
        pass


class ExchangedStickerService(Service):
    """
    Service class for exchanged sticker.
    """

    def __init__(self, model) -> None:
        super().__init__(model)


sticker_service = StickerService(Sticker)
exchanged_sticker_service = ExchangedStickerService(ExchangedSticker)
