from sqlalchemy import update, select, func
from api.core.base.services import Service
from typing import Type, Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, Sequence, Union
from api.v1.user.model import User
from api.core.base.services import validate_params

class UserService(Service):
    """
    Service class for user management.
    """

    def __init__(self, model: Type[User]) -> None:
        super().__init__(model)

    async def fetch_user_by_field(
        self, 
        session: AsyncSession, 
        field: str, 
        value: str
    ) -> Optional[User]:
        """
        Fetch a user by a specified field (e.g., id or email).
        
        Args:
            session (AsyncSession): Database session.
            field (str): Field to filter by ('id' or 'email').
            value (Union[str, int]): Value of the field to filter by.
        
        Returns:
            Optional[User]: User object if found, otherwise None.
        """
        if field not in {"user_id", "email"}:
            raise ValueError("Invalid field. Allowed fields are 'id' and 'email'.")

        filterer = {field: value}
        return await self.fetch(filterer, session)

    async def fetch_all_active_users(
        self, filterer: dict, session: AsyncSession, where: dict = {}
    ) -> Sequence[User]:
        """
        Fetch all active users with pagination and filters.
        """
        where["is_active"] = True
        return await self.fetch_all(filterer, session, where)

    async def update_user(self, user_id: str, schema: dict, session: AsyncSession) -> Optional[User]:
        """
        Update user details.
        """
        schema = await validate_params(self.model, schema)
        stmt = update(self.model).where(self.model.id == user_id).values(**schema).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()
        updated_user = result.scalars().all()
        if updated_user:
            update_user = update_user[0]
            await session.refresh(updated_user)
            return updated_user
        return None

    async def soft_delete_user(self, user_id: str, session: AsyncSession) -> Optional[User]:
        """
        Soft delete a user by marking them as inactive.
        """
        stmt = update(self.model).where(self.model.id == user_id).values(is_active=False).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()
        deleted_user = result.scalars().unique().one_or_none()
        if deleted_user:
            await session.refresh(deleted_user)
        return deleted_user

    async def fetch_user_roles(self, user_id: str, session: AsyncSession) -> Optional[User]:
        """
        Fetch user along with roles.
        """
        stmt = select(self.model).options(selectinload(self.model.roles)).where(self.model.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def count_active_users(self, session: AsyncSession) -> int:
        """
        Count active users in the system.
        """
        stmt = select(func.count()).select_from(self.model).where(self.model.is_active == True)
        result = await session.execute(stmt)
        count = result.scalars().unique().one_or_none()
        return count if count is not None else 0


user_service = UserService(User)
