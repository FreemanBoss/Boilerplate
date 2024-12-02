from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from api.database.database import get_async_session
from api.v1.user.schema import (
    UserCreateSchema,
    UserUpdateSchema,
    UserDataSchema,
    PaginatedUsersResponse,
    ActiveUserCountSchema,
)
from api.utils.responses_schema import responses
from api.v1.user.service import user_service
from api.v1.auth.dependencies import oauth2_scheme, verify_token

user = APIRouter(prefix="/users", tags=["User Management"])

@user.get(
    "/count",
    response_model=ActiveUserCountSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
async def count_active_users(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Count all active users in the system.
    """
    decoded = await verify_token(access_token, request, "access")
    active_user_count = await user_service.count_active_users(session=session)
    return {"message": "Active user count retrieved successfully.", "data": active_user_count}


@user.get(
    "/{user_id}",
    response_model=UserDataSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
async def get_user(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Retrieve a user by their ID.
    """
    user = await user_service.fetch_user_by_field(session, field="user_id", value=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return user


@user.get(
    "/",
    response_model=PaginatedUsersResponse,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
async def get_all_users(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[str, Depends(oauth2_scheme)],
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
):
    """
    Retrieve all active users with pagination.
    """
    filterer = {"page": page, "limit": page_size}
    users = await user_service.fetch_all_active_users(filterer, session)
    return users


@user.patch(
    "/{user_id}",
    response_model=UserDataSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
async def update_user(
    user_id: str,
    user_data: UserUpdateSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Update a user's details.
    """
    updated_user = await user_service.update_user(user_id=user_id, schema=user_data.dict(), session=session)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return updated_user


@user.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "User successfully deactivated (soft delete)."},
        404: {"description": "User not found."},
    },
)
async def delete_user(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Deactivate (soft delete) a user by their ID.
    """
    deleted_user = await user_service.soft_delete_user(user_id=user_id, session=session)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )


@user.get(
    "/{user_id}/roles",
    response_model=UserDataSchema,
    status_code=status.HTTP_200_OK,
    responses=responses,
)
async def fetch_user_roles(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Retrieve user roles along with user details.
    """
    user_with_roles = await user_service.fetch_user_roles(user_id=user_id, session=session)
    if not user_with_roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return user_with_roles
