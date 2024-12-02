from typing import Annotated
from fastapi import (
    APIRouter,
    status,
    Depends,
    Request,
    Query,
    File,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.auth.dependencies import oauth2_scheme
from api.v1.verification_request.schema import (
    UpdateVerificationOutputSchema,
    UpdateVerificationSchema,
    AllVerificationRequestOutSchema,
    VerificationOutSchema,
    FetchVerificationOutputSchema,
)
from api.v1.verification_request.service import verification_request_service


logger = create_logger("Verification route Route")


verification = APIRouter(prefix="/verifications", tags=["VERIFICATIONS"])


@verification.put(
    "/{verification_id}",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=UpdateVerificationOutputSchema,
)
async def update_verification(
    verification_id: str,
    request: Request,
    schema: UpdateVerificationSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Updates a verification request."""
    return await verification_request_service.update_verification(
        schema=schema,
        session=session,
        request=request,
        access_token=access_token,
        verification_id=verification_id,
    )


@verification.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AllVerificationRequestOutSchema,
    responses=responses,
)
async def fetch_verifications(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    page: int = Query(default=1, examples=[1]),
    limit: int = Query(default=10, examples=[10]),
    sort_order: str = Query(default="desc", examples=["desc", "asc"], strict=True),
    sort: str = Query(
        default="created_at", examples=["created_at", "updated_at"], strict=True
    ),
    status: str = Query(default=None, examples=["rejected"]),
):
    """Updates a role."""
    valid_params = {
        "page": page,
        "limit": limit,
        "sort_order": sort_order,
        "sort": sort,
        "status": status,
    }
    return await verification_request_service.retrieve_all_verifications(
        params=valid_params,
        session=session,
        request=request,
        access_token=access_token,
    )


@verification.post(
    "/request",
    status_code=status.HTTP_201_CREATED,
    response_model=VerificationOutSchema,
    responses=responses,
)
async def apply_for_verification(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    photo: Annotated[UploadFile, File(description="A file read as bytes")],
):
    """Applies for a verification request"""

    return await verification_request_service.apply_for_verification(
        photo,
        session=session,
        request=request,
        access_token=access_token,
    )


@verification.get(
    "/request",
    status_code=status.HTTP_200_OK,
    response_model=FetchVerificationOutputSchema,
    responses=responses,
)
async def check_verification_status(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """Applies for a verification request"""

    return await verification_request_service.get_verification_status(
        session=session,
        request=request,
        access_token=access_token,
    )
