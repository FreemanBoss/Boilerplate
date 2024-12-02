from typing import Annotated
from fastapi import APIRouter, status, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.role_and_permission.schema import (
    UpdateRoleSchema,
    RolesOutputSchema,
    UpdateRolesOutputSchema,
    CreateRoleSchema,
    CreateRolesOutputSchema,
)
from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.role_and_permission.service import role_service
from api.v1.auth.dependencies import oauth2_scheme


logger = create_logger("Roles Route")

role_and_permission = APIRouter(prefix="/roles", tags=["ROLES"])


@role_and_permission.post(
    "",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=CreateRolesOutputSchema,
)
async def create_new_role(
    request: Request,
    schema: CreateRoleSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """creates a new role."""
    return await role_service.create_role_and_permission(
        schema=schema,
        session=session,
        request=request,
        access_token=access_token,
    )


@role_and_permission.put(
    "/{role_id}",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=UpdateRolesOutputSchema,
)
async def update_role(
    role_id: str,
    request: Request,
    schema: UpdateRoleSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Updates a role."""
    return await role_service.update_role(
        schema=schema,
        session=session,
        request=request,
        access_token=access_token,
        role_id=role_id,
    )


@role_and_permission.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=RolesOutputSchema,
    responses=responses,
)
async def fetch_role(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    page: int = Query(default=1, examples=[1]),
    limit: int = Query(default=10, examples=[10]),
    sort_order: str = Query(default="desc", examples=["desc", "asc"], strict=True),
    sort: str = Query(
        default="created_at", examples=["created_at", "updated_at"], strict=True
    ),
):
    """Updates a role."""
    valid_params = {
        "page": page,
        "limit": limit,
        "sort_order": sort_order,
        "sort": sort,
    }
    return await role_service.retrieve_all_roles(
        params=valid_params,
        session=session,
        request=request,
        access_token=access_token,
    )
