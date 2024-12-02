from typing import List, Annotated, Optional
import re
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator, StringConstraints
from bleach import clean


class PermissionBase(BaseModel):
    """
    Schema base for permission.
    """

    id: str = Field(examples=["i2foecvwvkrom.v3rv qv3.vqevvecdve"])
    name: str = Field(examples=["create_user"])
    description: str = Field(examples=["Can create new users"])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])


class RolePermissionBase(BaseModel):
    """
    Schema for role_permission.
    """

    id: str = Field(examples=["i2foecvwvkrom.v3rv qv3.vqevvecdve"])
    name: str = Field(examples=["superadmin"])
    description: str = Field(examples=["Administrator with all permissions"])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    permissions: List[PermissionBase]


# ------------------------------------------------------------------------------


class RolesOutputSchema(BaseModel):
    """
    Schema for roles response
    """

    status_code: int = Field(default=200, examples=[200])
    page: int
    limit: int
    total_pages: int
    total_items: int
    message: str = Field(
        default="Roles Retrieved Successfully.",
        examples=["Roles Retrieved Successfully."],
    )
    data: List[RolePermissionBase]


# -----------------------------------------------------------------------
# CREATE


class CreateRolesOutputSchema(BaseModel):
    """
    Schema for roles response
    """

    status_code: int = Field(default=201, examples=[201])
    message: str = Field(
        default="Roles Created Successfully.",
        examples=["Roles Created Successfully."],
    )
    data: RolePermissionBase


class CreatePermissionSchema(BaseModel):
    """
    Schema base for permission update.
    """

    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["create_user"])
    description: Annotated[
        str,
        StringConstraints(
            min_length=10, max_length=50, strip_whitespace=True, strict=True
        ),
    ] = Field(examples=["Can create new users"])

    @model_validator(mode="before")
    @classmethod
    def validate_fiels(cls, values: dict):
        """
        Validates fields.
        """
        return validate_fiels(values.get("name", ""), values.get("description", ""))


class CreateRoleSchema(BaseModel):
    """
    Update role schema.
    """

    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["create_user"])
    description: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["Can create new users"])
    permissions: List[CreatePermissionSchema]

    @model_validator(mode="before")
    @classmethod
    def validate_fiels(cls, values: dict):
        """
        Validates fields.
        """
        values["name"] = clean(values.get("name", ""))
        values["description"] = clean(values.get("description", ""))
        return values


# ------------------------------------------------------------------------------
# UPDATE
class UpdateRolesOutputSchema(BaseModel):
    """
    Schema for roles response
    """

    status_code: int = Field(default=201, examples=[201])
    message: str = Field(
        default="Roles Updated Successfully.",
        examples=["Roles Updated Successfully."],
    )
    data: RolePermissionBase


class UpdatePermissionSchema(BaseModel):
    """
    Schema base for permission update.
    """

    id: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["0193010f-572a-729c-9817-2b78640c6a20"])
    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["edit_user"])
    description: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["Can edit new users"])

    @model_validator(mode="before")
    @classmethod
    def validate_fiels(cls, values: dict):
        """
        Validates fields.
        """
        values.update(
            validate_fiels(values.pop("name", ""), values.pop("description", ""))
        )
        return values


class UpdateRoleSchema(BaseModel):
    """
    Update role schema.
    """

    id: Optional[str] = Field(
        default=None, examples=["0193010f-572a-729c-9817-2b78640c6a20"]
    )
    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["admin"])
    description: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=3, max_length=50, strict=True
        ),
    ] = Field(examples=["Admin with partial permissions"])
    permissions: List[UpdatePermissionSchema]

    @model_validator(mode="before")
    @classmethod
    def validate_fiels(cls, values: dict):
        """
        Validates fields.
        """
        values["name"] = clean(values.get("name", ""))
        values["description"] = clean(values.get("description", ""))
        return values


# ---------------------------------------------------------------
# VALIDATION
def validate_fiels(name: str, description: str) -> dict:
    """
    Validates fields.
    """

    if not name or not description:
        raise ValueError("must provide name and description of the role")

    pattern = r"^(?=.*_)[A-Za-z_]{1,50}$"

    if not re.match(pattern=pattern, string=name):
        raise ValueError(f"{name} must be separated by a single underscore.")

    name = clean(name)
    description = clean(description)

    return {"name": name, "description": description}
