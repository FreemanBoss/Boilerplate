from typing import Annotated
from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.schema import (
    RegisterSuperadminSchema,
    RegisterOutputSchema,
)
from api.v1.auth.dependencies import get_current_active_superadmin, User
from api.v1.auth.schema import RegisterStaffSchema
from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.superadmin.service import superadmin_service


logger = create_logger("Superadmin Route")

superadmin = APIRouter(prefix="/superadmin", tags=["SUPERADMIN"])


@superadmin.post(
    "/register",
    response_model=RegisterOutputSchema,
    responses=responses,
    status_code=status.HTTP_201_CREATED,
)
async def register_superadmin(
    request: Request,
    schema: RegisterSuperadminSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Registers a new superuser.

        Keyword arguments:
            schema -- Fields containing the superuser details to register
        Return: A response containing the newly created user details and success message.
        Raises: HTTPException if email already exists or secret is invalid.
        Raises: Validation Error if any field is invalid.
        Raise: Internal Server Error if any other process goes wrong
    """
    return await superadmin_service.register(
        schema=schema, session=session, request=request
    )


@superadmin.post(
    "/users/register",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=RegisterOutputSchema,
)
async def register_users(
    schema: RegisterStaffSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_superadmin: Annotated[User, Depends(get_current_active_superadmin)],
):
    """
    Endpoint for superadmin to register other users.

    :param schema: Request body containing email, role, password, and confirm_password
    :param session: AsyncSession dependency for database access
    :return: Success message upon successful registration
    """
    return await superadmin_service.register_users(
        schema.model_dump(exclude={"confirm_password"}),
        session,
        current_superadmin.secret_token_identifier,
    )
