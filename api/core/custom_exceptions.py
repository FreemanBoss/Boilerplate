"""
CUstom Exception module.
"""
from typing import Any


class UserNotFoundError(Exception):
    """
    Custom error for user not found.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        message = "User not found."
        super().__init__(message, *args, **kwargs)


class EmailAlreadyExistsError(Exception):
    """
    Custom error for email already exists.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        message = "Email already exists."
        super().__init__(message, *args, **kwargs)


class InvalidEmailOrPasswordError(Exception):
    """
    Custom error for invalid email or password.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        message = "Invalid email or password."
        super().__init__(message, *args, **kwargs)


class UserNotAdminError(Exception):
    """
    Custom error for User is not authorized.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        message = "User is not authorized for this action."
        super().__init__(message, *args, **kwargs)
