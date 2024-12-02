from typing import Annotated, List, Optional
from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Request,
    File,
    UploadFile,
    Path,
    Query,
    Body,
)
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.setting.schema import SettingsUpdateRequest, SettingsResponse
from api.v1.setting.service import setting_service
from api.v1.user_block.schema import (
    CreateUserBlockResponse,
    UserBlockCreate,
    DeleteBlockResponse,
    AllUserBlockResponse,
)
from api.v1.profile.schema import (
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    UpdateResponseSchema,
    ProfileUpdateSchema,
    FetchProfileResponseSchema,
    DeleteUserResponse,
)
from api.v1.photo.schema import (
    CreateProfilePhotoResponse,
    ReplaceProfilePhotoResponse,
    CreateProfilePhotoRequest,
)
from api.v1.user.model import User

from api.database.database import get_async_session
from api.utils.task_logger import create_logger
from api.utils.responses_schema import responses
from api.v1.auth.dependencies import get_current_active_user, oauth2_scheme
from api.v1.profile.service import profile_service
from api.v1.photo.service import profile_photo_service
from api.v1.user_block.service import user_block_service

logger = create_logger("Profile Route")

profiles = APIRouter(prefix="/profiles", tags=["PROFILE"])


@profiles.post(
    "",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=ProfileUpdateResponse,
)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Updates a users profile.

    Args:
        profile_data(object): pydantic model.
    Returns:
        ProfileUpdateResponse(object): contains profile data and success message if successful
    """

    return await profile_service.update_profile(profile_data, session, current_user)


@profiles.get(
    "/settings",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=SettingsResponse,
)
async def get_user_settings(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Fetches a users profile settings.

    Args:
        request(object): request object
        session(asyncsession): database async session object.
        access_token(str): request access token.
    Returns:
        SettingsResponse(object): contains settings data and success message if successful
    """

    return await setting_service.fetch_setting(request, session, access_token)


@profiles.get(
    "/{profile_id}",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=FetchProfileResponseSchema,
)
async def fetch_profile(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    profile_id: str,
):
    """
    Retrieves a users profile.

    Args:
        profile_data(object): pydantic model.
    Returns:
        FetchProfileResponseSchema(object): contains profile data and success message if successful
    """

    return await profile_service.fetch_profile(
        session=session, profile_id=profile_id, user_id=current_user.id
    )


@profiles.put(
    "/pictures/{photo_id}",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=ReplaceProfilePhotoResponse,
)
async def Replace_profile_photos(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    photo: Annotated[UploadFile, File(description="1 profile picture")],
    photo_id: str,
):
    """
    Updates/Changes a users profile photos.

    Args:
        photos(List(UploadFile)): list of the photos to upload
    Returns:
        CreateProfilePhotoResponse(object): contains pictures data and success message if successful
    """

    return await profile_photo_service.replace_a_profile_photo(
        request=request,
        session=session,
        photo=photo,
        access_token=access_token,
        photo_id=photo_id,
    )


@profiles.post(
    "/pictures",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=CreateProfilePhotoResponse,
)
async def upload_profile_photos(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    photos: Annotated[List[UploadFile], File(description="4 - 6 profile pictures")],
):
    """
    Uploads a users profile photos.

    Accepts minimum of 4 and maximum of 6 photos.

    Args:
        photos(List(UploadFile)): list of the photos to upload
    Returns:
        CreateProfilePhotoResponse(object): contains pictures data and success message if successful
    """

    return await profile_photo_service.create_profile_photo(
        request, session, photos, access_token
    )


@profiles.delete(
    "/settings",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=DeleteUserResponse,
)
async def soft_delete_user_account(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Soft delete a user account.

    Args:
        session(asyncsession): database async session object.
        current_user(User): the current authenticated user.
    Returns:
        DeleteUserResponse(object): contains success or error message
    """

    return await profile_service.soft_delete_user(session, current_user)


@profiles.post(
    "/settings/block-lists/{blocked_id}",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserBlockResponse,
)
async def block_user(
    request: Request,
    blocked_id: Annotated[
        str, Path(description="String identifier derived from the request URL")
    ],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    schema: Annotated[
        Optional[UserBlockCreate], Body(description="Optional reason for blocking")
    ] = None,
):
    """
    Blocks a user.

    Args:
        request(object): request object
        blocked_id(str): id of the user to block
        schema(object): pydantic model.
        session(asyncsession): database async session object.
        access_token(str): request access token.
    Returns:
        UserBlockCreate(object): contains success or error message
    """

    return await user_block_service.block_user(
        request, blocked_id, schema, session, access_token
    )


@profiles.get(
    "/settings/block-lists",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=AllUserBlockResponse,
)
async def get_blocked_users(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    page: Annotated[int, Query(examples=[1])] = 1,
    limit: Annotated[int, Query(examples=[10])] = 10,
):
    """
    Retrieves a paginated list of all profiles blocked by a user.

    Args:
        request(object): request object
        schema(object): pydantic model.
        session(asyncsession): database async session object.
        access_token(str): request access token.
    Returns:
        AllUserBlockResponse(object): contains success or error message
    """

    valid_params = {"page": page, "limit": limit}

    return await user_block_service.get_blocked_users(
        request, valid_params, session, access_token
    )


@profiles.delete(
    "/settings/block-lists/{blocked_id}",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=DeleteBlockResponse,
)
async def unblock_user(
    request: Request,
    blocked_id: Annotated[
        str, Path(description="String identifier derived from the request URL")
    ],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Unblocks a user.

    Args:
        request(object): request object
        blocked_id(str): id of the user to block
        session(asyncsession): database async session object.
        access_token(str): request access token.
    Returns:
        DeleteBlockResponse(object): contains success or error message
    """

    return await user_block_service.unblock_user(
        request, blocked_id, session, access_token
    )


@profiles.put(
    "/settings",
    responses=responses,
    status_code=status.HTTP_200_OK,
    response_model=SettingsResponse,
)
async def update_profile_settings(
    request: Request,
    schema: SettingsUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Updates a users profile settings.

    Args:
        request(object): request object
        schema(object): pydantic model.
        session(asyncsession): database async session object.
        access_token(str): request access token.
    Returns:
        SettingsResponse(object): contains settings data and success message if successful
    """

    return await setting_service.update_settings(request, schema, session, access_token)


@profiles.put(
    "/{profile_id}",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    response_model=UpdateResponseSchema,
)
async def update_profile_fields(
    profile_data: ProfileUpdateSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    profile_id: str,
):
    """
    Updates a users profile individual fields.

    Args:
        profile_data(object): pydantic model.
    Returns:
        ProfileUpdateSchema(object): contains profile data and success message if successful
    """

    return await profile_service.update_profile_fields(
        schema=profile_data,
        session=session,
        profile_id=profile_id,
        user_id=current_user.id,
    )
