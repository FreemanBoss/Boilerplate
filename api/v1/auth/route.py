from typing import Annotated
from fastapi import APIRouter, status, Request, Depends, Query, HTTPException, Header, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.schema import (
    RegisterOutputSchema,
    LoginOutputSchema,
    LoginShema,
    ResendVerificationSchema,
    ResendVerificationOutputSchema,
    EmailVerificationOutputSchema,
    AccessToken,
    ResetPasswordResponse,
    ResetPasswordSuccesful,
    ResetPasswordRequest,
    RequestEmail

)
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.responses import Response
from api.database.database import get_async_session
from api.v1.auth.service import auth_service
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.auth.passwd_reset_service import reset_password_service
from api.utils.celery_setup.tasks import send_email
from api.v1.auth.schema import UserCreate
import json
from api.v1.auth.dependencies import oauth2_scheme


logger = create_logger("Auth Route")

auth = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])

@auth.post("/request-password-reset", status_code=status.HTTP_200_OK,
                response_model=ResetPasswordResponse)
async def request_reset_link(
    reset_email: RequestEmail,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_async_session)],
):
    """
    Generates a link for resetting password for a user.
        Args:
            reset_email: The request body containing the data
            background_tasks: The Background task method.
            db: the database Session object.
        Retuns:
            Response: response containing a successful message.
        Raises:
            HTTPException: If anything goes wrong
    """
    user = await reset_password_service.fetch(reset_email.email, db)
    reset_token = await reset_password_service.create(user, db)
   
    try:
        background_tasks.add_task(
            send_email,
            recipient=user.email,
            template_name="reset-password.html",
            subject="Password Reset",
            context={
                "first_name": user.first_name,
                "last_name": user.last_name,
                # "link": link
            }
        )
       
        return ResetPasswordResponse(
            message="Reset password link successfully sent to user",
            status_code=status.HTTP_200_OK
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth.patch("/verify-reset-token",
    status_code=status.HTTP_201_CREATED,
    response_model=ResetPasswordSuccesful
)
async def reset_password(
    reset_password_data: ResetPasswordRequest,
    db: Annotated[Session, Depends(get_async_session)]
):
    """
    Verifies and resets password for a user.

    Args:
        reset_password_data: The request body containing the data
        db: the database Session object.

    Returns:
        Response: response containing user information and access and refresh tokens

    Raises:
        HTTPException: If anything goes wrong
    """
    try:
        response_data, refresh_token = await reset_password_service.update(reset_password_data, db)
        response_body = response_data.model_dump()

        response_body["refresh_token"] = refresh_token

        return Response(
            content=json.dumps(response_body),
            status_code=status.HTTP_201_CREATED,
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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
    Verifies the user email after registration..

        Keyword arguments:
            token -- query params containing the token to verify
        Return: redirects a user to a deep link to their mobile app.
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
    Resends a verificationlink after the previous one has expired without confirmation.

        Keyword arguments:
            schema -- the payload with user email.
        Return: response message
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
    Logs in a superuser.

        Keyword arguments:
            schema -- Fields containing the user details to authorize
        Return: A response containing the status_code, message, token, and user data.
        Raises: HTTPException if password or email is invalid.
        Raises: Validation Error if any field is invalid.
        Raise: Internal Server Error if any other process goes wrong
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

    :param user_data: Request body containing email, password, and confirm_password
    :param session: AsyncSession dependency for database access
    :return: Success message upon successful registration
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

    Args:
        access_token (str): Bearer token from the authorization header.
    Returns:
        A success response if logout was successful, or error response otherwise.
    """
    # Extract token by removing "Bearer " prefix
    if not access_token or not access_token.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authentication required to log out"
        )

    access_token = access_token[7:]
    refresh_token = request.cookies.get(
        "refresh_token"
    )  # assuming refresh token is stored in a cookie

    if not refresh_token:
        raise HTTPException(
            status_code=401, detail="Authentication required to log out"
        )

    # Perform logout
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
    """Logs in a user on openai."""
    return await auth_service.oauth2_authenticate(
        email=form_data.username,
        password=form_data.password,
        session=session,
        request=request,
    )
