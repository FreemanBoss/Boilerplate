import os
import re
from fastapi import Request, HTTPException, UploadFile, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from api.core.base.services import Service
from api.v1.photo.model import Photo, ProfilePhoto
from api.v1.photo.schema import (
    CreateProfilePhotoResponse,
    ProfilePhotoBase,
    ReplaceProfilePhotoResponse,
    ReplaceProfilePhotoRequest,
)
from api.v1.auth.dependencies import authenticate_user, verify_token
from api.utils.upload_file import upload_file_to_cloudinary
from api.v1.profile.service import profile_service
from api.utils.settings import Config


class ProfilePhotoService(Service):
    """
    Service class for profile photo resource.
    """

    def __init__(self, model) -> None:
        """
        Constructor
        """
        super().__init__(model)

    async def create_profile_photo(
        self,
        request: Request,
        session: AsyncSession,
        photos: List[UploadFile],
        access_token: str,
    ) -> Optional[CreateProfilePhotoResponse]:
        """Creates users profile photo

        Args:
            request(object): request object
            session(asyncsession): database async session object.
            photos(List(UploadFile)): list of the photos to upload
            access_token(str): request token.
        Returns:
            CreateProfilePhotoResponse(object): contains pictures data and success message if successful
        """

        async with session.begin().session as session:
            claims = await authenticate_user(request, access_token)

            current_photos = await self.fetch_all(
                filterer={}, session=session, where={"user_id": claims.get("user_id")}
            )

            is_initial_upload = len(current_photos) == 0

            if is_initial_upload:
                # Initial photo upload validation (4-6 photos)
                if not 4 <= len(photos) <= 6:
                    raise HTTPException(
                        status_code=400,
                        detail="You must provide between 4 and 6 profile photos",
                    )
            else:
                # Additional photos validation (max 2 more)
                if len(photos) > 2:
                    raise HTTPException(
                        status_code=400,
                        detail="You can only add up to 2 additional photos",
                    )

                if len(current_photos) + len(photos) > 6:
                    remaining_slots = 6 - len(current_photos)
                    raise HTTPException(
                        status_code=400,
                        detail=f"You can only add {remaining_slots} more photo(s). You tried to add {len(photos)}",
                    )

            created_photos = []

            for index, photo in enumerate(photos):
                if photo.size > 2 * 1024 * 1024:  # 2 MB limit
                    raise HTTPException(
                        status_code=400, detail="File size exceeds the limit"
                    )

                content_types = {
                    "image/png",
                    "image/webp",
                    "image/svg+xml",
                    "image/bmp",
                    "image/tiff",
                }
                if photo.content_type not in content_types:
                    raise HTTPException(
                        status_code=415, detail="Unsupported file type."
                    )

                photo_name, ext = os.path.splitext(photo.filename)
                photo_name = re.sub(r"[^\w\-_\.]", "_", photo_name)
                photo_name = f"{photo_name}_{uuid4()}"

                if not Config.TEST:
                    # Upload photo to Cloudinary
                    photo_url = await upload_file_to_cloudinary(
                        file=photo,
                        folder="photos/profile_photos",
                        file_name=photo_name,
                        file_type="image",
                        product_id_prefix="profile_photos",
                    )
                else:
                    photo_url = "https://fakePhoto_url.com"

                # Create photo record in database
                photo_data = {
                    "user_id": claims.get("user_id"),
                    "url": photo_url,
                    "is_primary": index == 0
                    and is_initial_upload,  # Only first photo of initial upload is primary
                }

                created_photo = await self.create(photo_data, session)
                created_photos.append(
                    ProfilePhotoBase.model_validate(created_photo, from_attributes=True)
                )

            return CreateProfilePhotoResponse(
                message="Profile photos saved successfully.", data=created_photos
            )

    async def replace_a_profile_photo(
        self,
        photo: UploadFile,
        photo_id: str,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ):
        """
        Replaces an old profile photo with another.

        Args:
            photo(bytes): the photo to upload.
            session(AsyncSession): database session object.
            request(Request): Request object.
            access_token(str): access_token from Authorization Header
            photo_id(str): The photo to replace.
        Returns:
            ReplacePhotoOutSchema(pydantic): object conatin the response payload
        Raises:
            401 if Unauthorized.
            400 if file size too large.
            415 if file type is not valid
        """

        claims: dict | None = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        photo_exists = await self.fetch(
            {"user_id": claims.get("user_id"), "id": photo_id}, session
        )
        if not photo_exists:
            raise HTTPException(status_code=400, detail="Photo not found")

        if photo.size > 2 * 1024 * 1024:  # 2 MB limit
            raise HTTPException(status_code=400, detail="File size exceeds the limit")
        content_types = {
            "image/png",
            "image/webp",
            "image/svg+xml",
            "image/bmp",
            "image/tiff",
        }
        if photo.content_type not in content_types:
            raise HTTPException(status_code=415, detail="Unsupported file type.")

        photo_name, ext = os.path.splitext(photo.filename)
        photo_name = re.sub(r"[^\w\-_\.]", "_", photo_name)
        # photo_name = f"{photo_name}_{uuid4()}{ext}"
        photo_name = f"user_{claims.get('user_id')}_{uuid4()}"

        # Upload photo to cloud storage
        if not Config.TEST:
            photo_url = await upload_file_to_cloudinary(
                file=photo,
                folder="photos/profile_photos",
                file_name=photo_name,
                file_type="image",
                product_id_prefix="profile_photos",
            )
        else:
            photo_url = "https://fakePhoto_url.com"

        photo_exists.url = photo_url

        await session.commit()
        await session.refresh(photo_exists)

        return ReplaceProfilePhotoResponse(
            data=ProfilePhotoBase.model_validate(photo_exists, from_attributes=True)
        )


profile_photo_service = ProfilePhotoService(ProfilePhoto)


class PhotoService(Service):
    """
    Service class for photo resource.
    """

    def __init__(self, model) -> None:
        """
        Constructor
        """
        super().__init__(model)


photo_service = PhotoService(Photo)
