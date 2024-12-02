"""
pydantic models
"""
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    constr
)


class UserBase(BaseModel):
    """
    User Base model
    """

    id: str = Field(examples=["1234ed.4455tf..."])
    email: str = Field(examples=["Johnson@example.com"])
    first_name: Optional[str] = Field(examples=["Johnson"])
    last_name: Optional[str] = Field(examples=["Doe"])
    created_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(examples=[datetime.now(timezone.utc)])
    email_verified: bool = Field(examples=[False])
    roles: List[str] = Field(examples=[["user"], ["superadmin"], ["admin"]])
    is_suspended: Optional[bool] = Field(examples=[False])
    is_deleted: bool = Field(examples=[False])

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    '''The schema for creating a user'''
    email: EmailStr = Field(..., description="User's email address, unique identifier")
    password: constr(min_length=8) = Field(..., description="Password for user account")
    first_name: Optional[constr(max_length=50)] = Field(None, description="User's first name")
    last_name: Optional[constr(max_length=50)] = Field(None, description="User's last name")
    date_of_birth: Optional[datetime] = Field(None,
    description="User's date of birth for age verification")
    location: Optional[str] = Field(None, description="User's location for proximity matches")
    bio: Optional[str] = Field(None, description="Short bio about the user")


    class Config:
        '''Config'''
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strong_password",
                "first_name": "Jane",
                "last_name": "Doe",
                "date_of_birth": "1990-05-24",
                "location": "New York, NY",
                "bio": "Love hiking and outdoor adventures!",
            }
        }


class UserUpdateSchema(BaseModel):
    '''The schema for updating user's information'''
    first_name: Optional[constr(max_length=50)] = Field(None, description="User's updated first name")
    last_name: Optional[constr(max_length=50)] = Field(None, description="User's updated last name")
    password: Optional[constr(min_length=8)] = Field(None,
    description="Updated password for user account")
    bio: Optional[str] = Field(None, description="Updated bio about the user")
    location: Optional[str] = Field(None, description="Updated location for proximity matches")
    interests: Optional[List[str]] = Field(None, description="User's updated interests")


    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "password": "new_secure_password",
                "bio": "I enjoy cooking and traveling the world.",
                "location": "San Francisco, CA",
                "interests": ["cooking", "traveling", "reading"],
            }
        }


class UserDataSchema(BaseModel):
    '''schema to retrieve user information'''
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_verified: bool
    is_active: bool
    is_suspended: bool
    date_of_birth: Optional[datetime] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[List[str]] = None
    last_login: Optional[datetime] = None


    class Config:
        '''Config'''
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "email_verified": True,
                "is_active": True,
                "is_suspended": False,
                "date_of_birth": "1990-05-24",
                "location": "New York, NY",
                "bio": "Love hiking and outdoor adventures!",
                "interests": ["hiking", "outdoor adventures", "reading"],
                "last_login": "2024-10-01T12:34:56Z",
            }
        }


class PaginatedUsersResponse(BaseModel):
    '''pagination structure for returning all users information'''
    total: int = Field(..., description="Total number of users available")
    page: int = Field(..., description="Current page number")
    size: int = Field(...,
    description="Number of users per page")
    results: List[UserDataSchema] = Field(...,
    description="List of user profiles for the current page")


    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "size": 20,
                "results": [
                    {
                        "id": 123,
                        "email": "user1@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "email_verified": True,
                        "is_active": True,
                        "is_suspended": False,
                        "date_of_birth": "1990-05-24",
                        "location": "New York, NY",
                        "bio": "Love hiking and outdoor adventures!",
                        "interests": ["hiking", "outdoor adventures"],
                        "last_login": "2024-10-01T12:34:56Z",
                    },
                    {
                        "id": 124,
                        "email": "user2@example.com",
                        "first_name": "John",
                        "last_name": "Smith",
                        "email_verified": True,
                        "is_active": True,
                        "is_suspended": False,
                        "date_of_birth": "1985-03-17",
                        "location": "San Francisco, CA",
                        "bio": "Passionate about tech and gaming.",
                        "interests": ["tech", "gaming"],
                        "last_login": "2024-10-01T13:47:12Z",
                    },
                ],
            }
        }

class ActiveUserCountSchema(BaseModel):
    message: str
    data: int
