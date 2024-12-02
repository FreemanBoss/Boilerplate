from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError
from api.database.database import get_async_session
from api.v1.user.model import User
from api.v1.auth.model import PasswordResetToken
from api.v1.auth.schema import (
    ResetPasswordRequest, ResetPasswordSuccesful
)
from api.v1.user.schema import UserBase
from sqlalchemy import delete   
from typing import Annotated
from api.utils.settings import Config
from api.core.base.services import Service
from api.v1.user.service import user_service

SECRET_KEY = Config.JWT_SECRET
ALGORITHM = Config.JWT_ALGORITHM

class RequestPasswordService(Service):
    def __init__(self):
        # Initialize with the User model or the intended model
        super().__init__(model=User)

    async def fetch(self, email: str, db: Annotated[AsyncSession, Depends(get_async_session)]):
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalars().unique().one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def create(self, user: User, db: Annotated[AsyncSession, Depends(get_async_session)]):
        await db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
        reset_token = PasswordResetToken(user_id=user.id, jti=user.id)
        db.add(reset_token)
        await db.commit()
        return self.generate_password_reset_token(user)

    def generate_password_reset_token(self, user: User):
        now = datetime.utcnow()
        expire = now + timedelta(minutes=5)
        payload = {"email": user.email, "jti": user.id, "iat": now, "exp": expire}
        return jwt.encode(claims=payload, key=SECRET_KEY, algorithm=ALGORITHM)

    async def update(self, reset_password_data: ResetPasswordRequest, db: Annotated[AsyncSession, Depends(get_async_session)]):
        payload = self.verify_reset_token(reset_password_data.reset_token)
        email = payload.get("email")
        jti = payload.get('jti')

        token_query = select(PasswordResetToken).where(PasswordResetToken.jti == jti)
        token_result = await db.execute(token_query)
        user_token = token_result.scalars().one_or_none()

        if user_token:
            access_token = user_service.create_access_token(user_token.user_id)
            refresh_token = user_service.create_refresh_token(user_token.user_id)
            hashed_password = user_service.hash_password(reset_password_data.new_password)

            user_query = select(User).where(User.id == user_token.user_id, User.email == email)
            user_result = await db.execute(user_query)
            user = user_result.scalars().one_or_none()

            if not user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            user.password = hashed_password
            await db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="reset_token already used")

    async def delete(self, user_token: PasswordResetToken, db: Annotated[AsyncSession, Depends(get_async_session)]):
        await db.delete(user_token)
        await db.commit()

    def get_reset_token_response(self, access_token: str, user: User):
        user_data = UserBase.model_validate(user, from_attributes=True)
        return ResetPasswordSuccesful(
            message='password successfully reset',
            status_code=status.HTTP_201_CREATED,
            access_token=access_token,
            data={"user": user_data}
        )

    def verify_reset_token(self, reset_token: str):
        try:
            return jwt.decode(reset_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reset token invalid")

reset_password_service = RequestPasswordService()
