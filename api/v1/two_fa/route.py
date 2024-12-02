from typing import Annotated, Optional
from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.user.model import User
from api.v1.auth.schema import LoginOutputSchema
from api.utils.responses_schema import responses
from api.database.database import get_async_session
from api.v1.auth.dependencies import get_current_active_user
from api.v1.two_fa.service import two_factor_service
from api.v1.two_fa.schema import(
    TwoFactorLoginVerifySchema,
    TwoFactorSetupOutputSchema,
    TwoFactorSetupSchema,
    TwoFactorVerifySchema,
    TwoFactorVerifyOutputSchema
)

two_factor = APIRouter(prefix="/2FA", tags=["AUTHENTICATION"])

@two_factor.post(
    "/setup",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=TwoFactorSetupOutputSchema
)
async def setup_2fa(
    request: Request,
    schema: TwoFactorSetupSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Optional[TwoFactorSetupOutputSchema]:
    """Initialize 2FA setup for a mobile device

    Args:
        request (Request): the request object
        schema (TwoFactorSetupSchema): request payload
        session (Annotated[AsyncSession, Depends): database session
        current_user (Annotated[User, Depends): current authenticated user

    Returns:
        Optional[TwoFactorSetupOutputSchema]: contains success message and data
    """

    return await two_factor_service.setup_2fa(
        request,
        schema,
        session,
        current_user
    )
    
    
@two_factor.post(
    "/verify-setup",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=TwoFactorVerifyOutputSchema
)
async def verify_2fa_setup(
    request: Request,
    schema: TwoFactorVerifySchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Optional[TwoFactorVerifyOutputSchema]:
    """Verify and complete 2FA setup

    Args:
        request (Request): request object
        schema (TwoFactorVerifySchema): request payload
        session (Annotated[AsyncSession, Depends): database session
        current_user (Annotated[User, Depends): authenticated user

    Returns:
        Optional[TwoFactorVerifyOutputSchema]: success response
    """

    return await two_factor_service.verify_setup(
        request,
        schema,
        session,
        current_user
    )


@two_factor.post(
    "/verify-login",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=LoginOutputSchema
)
async def verify_2fa_login(
    request: Request,
    schema: TwoFactorLoginVerifySchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Optional[LoginOutputSchema]:
    """Verify 2FA code and optionally trust device

    Args:
        request (Request): request object
        schema (TwoFactorLoginVerifySchema): request payload
        session (Annotated[AsyncSession, Depends): database payload

    Returns:
        Optional[LoginOutputSchema]: success response
    """

    return await two_factor_service.verify_login(request, schema, session)

