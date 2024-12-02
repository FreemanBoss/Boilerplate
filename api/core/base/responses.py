from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional, Dict

class BaseResponseData(BaseModel):
    """Base schema for response data"""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class BaseResponse(BaseModel):
    """Base schema for API responses"""

    status_code: int = Field(examples=[200], default=200)
    message: Optional[str] = Field(examples=["API response generated successfully."])
    data: Optional[Dict[str, Any]] = Field(default={}, examples=[{}])