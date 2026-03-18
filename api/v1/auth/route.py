from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_async_session
from api.utils.celery_setup.tasks import send_email
from api.utils.responses_schema import responses
from api.utils.task_logger import create_logger
from api.v1.auth.passwd_reset_service import reset_password_service
from api.v1.auth.schema import (
    AccessToken,
    EmailVerificationOutputSchema,
    LoginOutputSchema,
    LoginShema,
    RegisterOutputSchema,
    RequestEmail,
    ResendVerificationOutputSchema,
    ResendVerificationSchema,
    ResetPasswordRequest,
    ResetPasswordResponse,
    ResetPasswordSuccesful,
    UserCreate,
)
from api.v1.auth.service import auth_service

logger = create_logger("Auth Route")

auth = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])


@auth.post(
    "/request-password-reset",
    status_code=status.HTTP_200_OK,
    response_model=ResetPasswordResponse,
)
async def request_reset_link(
    reset_email: RequestEmail,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Generates and sends a password reset link for a user.
    """
    user = await reset_password_service.fetch(reset_email.email, db)
    reset_token = await reset_password_service.create(user, db)

    try:
        send_email.delay(
            context={
                "recipient_email": user.email,
                "template_name": "reset-password.html",
                "subject": "Password Reset",
                "first_name": user.first_name,
                "last_name": user.last_name,
                "link": reset_token,
            }
        )
        return ResetPasswordResponse(
            message="Reset password link successfully sent to user",
            status_code=status.HTTP_200_OK,
        )
    except Exception:
        logger.error("Failed to queue password reset email", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth.patch(
    "/verify-reset-token",
    status_code=status.HTTP_201_CREATED,
    response_model=ResetPasswordSuccesful,
)
async def reset_password(
    reset_password_data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Verifies password reset token and updates the user's password.
    """
    try:
        response_data, _refresh_token = await reset_password_service.update(
            reset_password_data, db
        )
        return response_data
    except HTTPException:
        raise
    except Exception:
        logger.error("Password reset failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred",
        )


# TODO: ask mobile devs for deep linking link
@auth.get(
    "/verify-email",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=EmailVerificationOutputSchema,
)
async def verify_registration_email(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    request: Request,
    token: str = Query(min_length=30),
):
    """
    Verifies the user email after registration.
    """
    return await auth_service.verify_email(token, session, request)


# TODO: ask mobile devs for deep linking link
@auth.post(
    "/resend-verification-link",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=ResendVerificationOutputSchema,
)
async def resend_verification_link(
    schema: ResendVerificationSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Resends a verification link after the previous one expires.
    """
    return await auth_service.resend_verification_email(schema.email, session)


@auth.post(
    "/login",
    response_model=LoginOutputSchema,
    responses=responses,
    status_code=status.HTTP_200_OK,
)
async def login_user(
    request: Request,
    schema: LoginShema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Authenticates a user with email and password.
    """
    return await auth_service.authenticate(
        schema=schema, session=session, request=request
    )


@auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=RegisterOutputSchema,
)
async def register_user(
    user_data: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Endpoint for user registration with email and password.
    """
    return await auth_service.register_regular_user(user_data, session)


@auth.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout Success"},
        401: {"description": "Unauthorized"},
        400: {"description": "Bad Request"},
    },
)
async def logout_user(
    request: Request,
    access_token: Annotated[str, Header(alias="Authorization")],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Logs out the user by invalidating the access and refresh tokens.
    """
    if not access_token or not access_token.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authentication required to log out"
        )

    access_token = access_token[7:]
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=401, detail="Authentication required to log out"
        )

    return await auth_service.logout_user(access_token, refresh_token)


@auth.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=AccessToken,
    include_in_schema=False,
)
async def token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """OAuth2 token endpoint."""
    return await auth_service.oauth2_authenticate(
        email=form_data.username,
        password=form_data.password,
        session=session,
        request=request,
    )
