from typing import List, Annotated, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator, StringConstraints, ConfigDict


class VerificationBase(BaseModel):
    """
    Schema base for verification.
    """

    id: str = Field(examples=["1234-567890987766-5554325346346-43767465"])
    user_to_verify_id: str = Field(
        examples=["1241234235-45435236563-45645647664-7567875"]
    )
    status: str = Field(examples=["pending"])
    verified_by_bot: bool = Field(examples=[False])
    verification_count: int = Field(examples=[1])
    verifier_feedback: Optional[str] = Field(examples=["Photo Irregularity."])
    photo_url: str = Field(
        examples=["https://aws.com/photos/verification_requests/johnson_image.png"]
    )
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------


class AllVerificationRequestOutSchema(BaseModel):
    """
    Schema for verifucation response
    """

    status_code: int = Field(default=200, examples=[200])
    page: int
    limit: int
    total_pages: int
    total_items: int
    message: str = Field(
        default="Verifications Retrieved Successfully.",
        examples=["Verifications Retrieved Successfully."],
    )
    data: List[VerificationBase]


# ------------------------------------------------------------------------------
# UPDATE
class UpdateVerificationOutputSchema(BaseModel):
    """
    Schema for Verification response
    """

    status_code: int = Field(default=201, examples=[201])
    message: str = Field(
        default="Verification Updated Successfully.",
        examples=["Verification Updated Successfully."],
    )
    data: VerificationBase


class UpdateVerificationSchema(BaseModel):
    """
    Schema base for verification update.
    """

    status: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=6, max_length=10, strict=True
        ),
    ] = Field(examples=["rejected"])

    @model_validator(mode="before")
    @classmethod
    def validate_fiels(cls, values: dict):
        """
        Validates fields.
        """
        status: str = values.get("status", "")
        if status not in ["approved", "rejected", "pending"]:
            raise ValueError(f"{status} must be either approved, rejected, or pending.")
        return values


# ----------------------------------------------------------------
class VerificationOutSchema(UpdateVerificationOutputSchema):
    """
    Schema for creating requests
    """

    message: str = Field(
        default="Verification requested Successfully.",
        examples=["Verification requested Successfully."],
    )


# -------------------------------------------------------
class FetchVerificationOutputSchema(UpdateVerificationOutputSchema):
    """
    Schema for Verification response
    """

    status_code: int = Field(default=200, examples=[200])
    message: str = Field(
        default="Verification Retrieved Successfully.",
        examples=["Verification Retrieved Successfully."],
    )
