"""
Exception handler module
"""

import time
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.utils.task_logger import create_logger

logger = create_logger(logger_name="Route middleware logger", backup_count=10)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log user IP, user agent, and route details on each request.
    Also checks for a valid user-agent.
    """

    async def dispatch(self, request: Request, call_next):
        user_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")

        # Check for missing user-agent
        if user_agent == "Unknown":
            logger.warning(
                "Request blocked due to missing user-agent", extra={"user_ip": user_ip}
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    {
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Bad Request: Missing user-agent header!",
                        "data": {},
                    }
                ),
            )

        # Log initial request info, masking sensitive information
        start_time = time.time()
        try:
            payload = await request.json()
            for sensitive_field in ["password", "confirm_password", "secret_token"]:
                if sensitive_field in payload:
                    payload[sensitive_field] = "************"
        except Exception:
            payload = {}
        logger.info(
            "Request received",
            extra={
                "user_ip": user_ip,
                "user_agent": user_agent,
                "path": request.url.path,
                "method": request.method,
                "payload": payload,
            },
        )

        # Retrieve authenticated user if available
        if not hasattr(request, "current_user"):
            request.current_user = None

        # Process the request
        response = await call_next(request)

        # Log response status and time taken
        process_time = time.time() - start_time
        user_info = (
            request.state.current_user
            if hasattr(request.state, "current_user")
            else "Guest"
        )

        logger.info(
            "Request completed",
            extra={
                "current_user": user_info,
                "user_ip": user_ip,
                "user_agent": user_agent,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "process_time": f"{process_time:.2f}s",
            },
        )

        return response


class SetHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Set header middleware class.
        """
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Sets the X-Frame-Options header to prevent the page from being
        # embedded in an iframe, protecting against clickjacking attacks.
        response.headers["X-Frame-Options"] = "DENY"
        # Sets the Expect-CT header, which enforces certificate transparency (CT).
        # It ensures that the site's SSL certificates are logged in public CT logs,
        # making it harder to use rogue certificates.
        response.headers["Expect-CT"] = "enforce; max-age=604800"
        # Sets the Referrer-Policy header to control how much of the referrer URL is shared when
        # navigating across sites. This can help limit exposure of sensitive information.
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Sets the X-XSS-Protection header to enable the browser's built-in XSS filter,
        # blocking content if an XSS attack is detected.
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


async def set_hsts_header(request: Request, call_next):
    """
    Sets the Strict-Transport-Security header to force the browser to communicate only over HTTPS.
    It prevents HTTP communication after the browser's first visit to the site.

    Key Header:
        Strict-Transport-Security:

        max-age: Enforce HTTPS for 1 year (31,536,000 seconds).
        includeSubDomains: Apply this rule to all subdomains as well.
        preload: Allows the site to be included in the browser's HSTS preload list, meaning it
                will default to HTTPS without needing a prior visit.
    """
    response = await call_next(request)

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )
    return response
