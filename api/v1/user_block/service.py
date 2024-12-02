import math
from fastapi import Request, HTTPException, status
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.base.services import Service
from api.utils.validate_pagination import validate_pagination

from api.v1.user.model import User
from api.v1.user_block.model import UserBlock
from api.v1.auth.dependencies import authenticate_user
from api.v1.user.service import user_service
from api.v1.user_block.schema import (
    UserBlockBase,
    UserBlockCreate,
    UserBlockResponse,
    CreateUserBlockResponse,
    AllUserBlockResponse,
    DeleteBlockResponse
)


class UserBlockService(Service):
    """
    Service class for profile.
    """
    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

    async def block_user(
        self,
        request: Request,
        blocked_id: str,
        schema: UserBlockCreate,
        session: AsyncSession,
        access_token: str
    ) -> Optional[CreateUserBlockResponse]:
        """Blocks a user

        Args:
            request(object): request object
            schema(object): pydantic model.
            session(asyncsession): database async session object.
            access_token(str): request token.
        Returns:
            CreateUserBlockResponse(object): contains block data and success message if successful
        """

        async with session.begin().session as session:

            claims = await authenticate_user(request, access_token)

            # Check if trying to block self
            if blocked_id == claims.get("user_id"):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot block yourself"
                )
            
            # Check if user to block exists
            blocked_user = await user_service.fetch(
                {"id": blocked_id},
                session
            )
            if not blocked_user:
                raise HTTPException(
                    status_code=404,
                    detail="User to block not found"
                )
            
            existing_block = await self.fetch(
                {"blocked_id": blocked_id, "blocker_id": claims.get("user_id")},
                session
            )
            
            if existing_block:
                raise HTTPException(
                    status_code=400,
                    detail="User is already blocked"
                )

            # Execute block
            block_data = {
                "blocker_id": claims.get("user_id"),
                "blocked_id": blocked_id,
            }
            if schema:
                if schema.reason:
                    block_data.update({"reason": schema.reason})

            new_block = await self.create(block_data, session)

            block_base = UserBlockBase.model_validate(new_block)

            return CreateUserBlockResponse(
                message="User successfully blocked.",
                data=block_base
            )


    async def unblock_user(
        self,
        request: Request,
        blocked_id: str,
        session: AsyncSession,
        access_token: str
    ) -> Optional[DeleteBlockResponse]:
        """Unblocks a user

        Args:
            request(object): request object
            session(asyncsession): database async session object.
            access_token(str): request token.
        Returns:
            DeleteBlockResponse(object): contains success or error message
        """

        async with session.begin().session as session:

            claims = await authenticate_user(request, access_token)

            # Check if trying to unblock self
            if blocked_id == claims.get("user_id"):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot unblock yourself"
                )

            stmt = (
                select(UserBlock)
                .join(User, User.id == blocked_id)
                .where(
                    UserBlock.blocked_id == blocked_id,
                    UserBlock.blocker_id == claims.get("user_id")
                    )
            )

            result = await session.execute(stmt)

            # If no block record is found, return 404
            block_record = result.scalars().first()
            if not block_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Block record not found or user is not blocked"
                )
            
            # delete block
            block_data = {
                "blocker_id": claims.get("user_id"),
                "blocked_id": blocked_id,
            }
            
            is_deleted = await self.delete(block_data, session)

            if is_deleted:
                return DeleteBlockResponse

            return DeleteBlockResponse(
                status_code=500,
                message="Unblock user failed."
            )


    async def get_blocked_users(
        self,
        request: Request,
        params: dict,
        session: AsyncSession,
        access_token: str
    ) -> Optional[AllUserBlockResponse]:
        """
        Fetches all blocked user.

        Args:
            request(object): request object
            params(object): query parameters.
            session(asyncsession): database async session object.
            access_token(str): request token.
        Returns:
            AllUserBlockResponse(object): contains list of all blocked users
        """

        async with session.begin().session as session:

            claims = await authenticate_user(request, access_token)

            # validate and sort params
            filtered_params = await validate_pagination(params)
            params_copy = filtered_params.copy()

            where = {}
            where.update({"blocker_id": claims.get("user_id")})
        
            blocked_users = await self.fetch_all(
                filterer=params, session=session, where=where
            )

            # Get the total number of blocked users
            count_stmt = (
                select(func.count())
                .select_from(UserBlock)
                .where(UserBlock.blocker_id == claims.get("user_id"))
            )
            count_result = await session.execute(count_stmt)
            total_blocked = count_result.scalar() or 0

            total_pages = 0
            if total_blocked > 0:
                total_pages = math.ceil(total_blocked / params_copy["limit"])

            return AllUserBlockResponse(
                message="Blocked list successfully generated",
                page=params_copy["page"],
                limit=params_copy["limit"],
                total_items=total_blocked,
                total_pages=total_pages,
                data=[
                    UserBlockBase.model_validate(block)
                    for block in blocked_users
                ]
            )


user_block_service = UserBlockService(UserBlock)
