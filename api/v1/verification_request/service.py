"""
Verification module
"""

import os
import re
import math
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException, Request, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.base.services import Service
from api.v1.verification_request.model import (
    VerificationRequest,
)
from api.v1.auth.dependencies import verify_token
from api.v1.verification_request.schema import (
    UpdateVerificationOutputSchema,
    UpdateVerificationSchema,
    AllVerificationRequestOutSchema,
    VerificationBase,
    FetchVerificationOutputSchema,
    VerificationOutSchema,
)
from api.v1.user.service import user_service
from api.utils.task_logger import create_logger
from api.utils.upload_file import (
    upload_file_to_cloudinary,
)
from api.utils.settings import Config
from api.utils.validate_pagination import validate_pagination


logger = create_logger("Role Service")


class VerificationRequestService(Service):
    """
    Service class for users verification requests.
    """

    def __init__(self, model) -> None:
        super().__init__(model)

    async def retrieve_all_verifications(
        self,
        params: dict,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[AllVerificationRequestOutSchema]:
        """
        Retrieves all verifications.

        Args:
            params(dict): dict containing pagination, sort, sort_order.
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode
        Returns:
            AllVerificationRequestOutSchema(pydantic model): retrieved verifications.
        """
        # authorize
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        claim_role = claims.get("role")
        if claim_role != "superadmin" and claim_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have enough permission to perform this action.",
            )

        # validate and sort params
        validated_params = await validate_pagination(params)

        where_clause = {}
        if params["status"]:
            where_clause.update({"status": params["status"]})
        del params

        # fetch roles and permissions
        params_copy = validated_params.copy()
        verifications = await self.fetch_all(
            where=where_clause, filterer=validated_params, session=session
        )

        verification_list = [
            VerificationBase.model_validate(verification, from_attributes=True)
            for verification in verifications
        ]
        total_items = await self.count(session)
        total_pages = 0

        if total_items > 0:
            total_pages = math.ceil(total_items / params_copy.get("limit"))

        return AllVerificationRequestOutSchema(
            page=params_copy["page"],
            limit=params_copy["limit"],
            total_pages=total_pages,
            total_items=total_items,
            data=verification_list,
        )

    async def update_verification(
        self,
        schema: UpdateVerificationSchema,
        session: AsyncSession,
        request: Request,
        access_token: str,
        verification_id: str,
    ) -> Optional[UpdateVerificationOutputSchema]:
        """
        Updates a verification request.

        Args:
            schema(pydantic model): object containing payload.
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode.
            verification_id(str): the id of the verification request to update.
        Returns:
            UpdateVerificationOutputSchema(pydantic model): Newly updated verification request.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        claim_role = claims.get("role")
        if claim_role != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have enough permission to perform this action.",
            )

        verification_request = await self.fetch({"id": verification_id}, session)

        if not verification_request:
            raise HTTPException(
                status_code=400, detail="verification_request not found"
            )
        if verification_request.status == "approved":
            return UpdateVerificationOutputSchema(
                message="Verification Already Approved",
                data=VerificationBase.model_validate(
                    verification_request, from_attributes=True
                ),
            )

        admin = await user_service.fetch({"id": claims.get("user_id")}, session)

        updated_verification = await self.update(
            [
                {
                    "id": verification_id,
                },
                {
                    "status": schema.status,
                    "verifier_id": admin.id,
                    "verification_count": verification_request.verification_count + 1,
                },
            ],
            session=session,
        )

        return UpdateVerificationOutputSchema(
            data=VerificationBase.model_validate(
                updated_verification, from_attributes=True
            )
        )

    async def apply_for_verification(
        self,
        photo: UploadFile,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[VerificationOutSchema]:
        """
        Validates verification requests and returns a response.

        Args:
            photo(bytes): the photo to upload.
            session(AsyncSession): database session object.
            request(Request): Request object.
            access_token(str): access_token from Authorization Header
        Returns:
            VerificationOutSchema(pydantic): object conatin the response payload
        Raises:
            401 if Unauthorized.
            400 if file size too large.
            415 if file type is not valid
        """
        claims: dict | None = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        if claims.get("role") != "user":
            raise HTTPException(status_code=401, detail="Access denied.")
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
        photo_name = f"{photo_name}_{uuid4()}"

        # Upload photo to cloud storage
        if not Config.TEST:
            photo_url = await upload_file_to_cloudinary(
                file=photo,
                folder="photos/verification_requests",
                file_name=photo_name,
                file_type="image",
                product_id_prefix="verification_requests",
            )
        else:
            photo_url = "https://fakePhoto_url.com"

        # save to database
        request_approved = await self.fetch(
            {"user_to_verify_id": claims.get("user_id"), "status": "approved"}, session
        )
        if request_approved:
            raise HTTPException(
                status_code=409, detail="Verification request already approved."
            )
        request_exists = await self.fetch(
            {"user_to_verify_id": claims.get("user_id")}, session
        )
        if request_exists:
            request_exists.verification_count += 1
            request_exists.status = "pending"
            request_exists.photo_url = photo_url
            request_exists.updated_at = datetime.now(timezone.utc)
            await session.commit()

        if not request_exists:
            new_request = await self.create(
                {
                    "user_to_verify_id": claims.get("user_id"),
                    "photo_url": photo_url,
                    "status": "pending",
                    "verification_count": 1,
                },
                session,
            )

        request_base = VerificationBase.model_validate(
            request_exists if request_exists else new_request, from_attributes=True
        )

        return VerificationOutSchema(
            message="Verification request created successfully.", data=request_base
        )

    async def get_verification_status(
        self,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[FetchVerificationOutputSchema]:
        """
        Retrieves verification status of a user.

        Args:
            session(AsyncSession): database session object.
            request(Request): Request object.
            access_token(str): access_token from Authorization Header
        Returns:
            FetchVerificationOutputSchema(pydntic): contains the verification status.
        """
        claims: dict | None = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        if claims.get("role") != "user":
            raise HTTPException(status_code=401, detail="Access denied.")

        request_exists = await self.fetch(
            {"user_to_verify_id": claims.get("user_id")}, session
        )
        if not request_exists:
            raise HTTPException(
                status_code=400, detail="verification request not found."
            )

        request_base = VerificationBase.model_validate(
            request_exists, from_attributes=True
        )

        return FetchVerificationOutputSchema(
            status_code=200,
            message="Verification Retrieved successfully.",
            data=request_base,
        )


verification_request_service = VerificationRequestService(VerificationRequest)
