from typing import Optional, Tuple, Union, Annotated
import dns.resolver
from fastapi import status, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import hashlib
import hmac


from api.utils.task_logger import create_logger
from api.utils.settings import Config
from api.v1.user.service import user_service
from api.v1.user import User
from api.v1.subscriptions.model import SubscriptionPlan, Subscription
from api.database.redis_database import get_redis_sync
from api.database.database import get_async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

logger = create_logger("::AUTH DEPENDENCY::")


async def generate_idempotency_key(email: str) -> str:
    """Creates an idempotency key

    Args:
        email(str): user email
    Return:
        Idempotency_key(str)
    """
    if not email:
        raise Exception("email not passed in generate_idempotency_key function.")
    the_date = date.today()
    key = f"{email}:{the_date}"
    idempotency_key: str = hashlib.sha256(key.encode()).hexdigest()
    return idempotency_key


async def check_idempotency_key(
    email: str, session: AsyncSession
) -> Union[None, object]:
    """
    Checks for idempotency by hashing email and date.

    Args:
        email(str): the email to use for idempotency check.
    Returns:
        user(object): if idempotency
        None: if not idempotency.
    """
    if not email:
        raise Exception("email not passed in check_existing_email function")
    key = await generate_idempotency_key(email)
    user = await user_service.fetch({"idempotency_key": key}, session)
    return user


async def get_current_user(
    access_token: str, request: Request, session: AsyncSession
) -> Optional[User]:
    """
    Retrieves the current user using the access_token.

    Args:
        access_token(str): access_token of the user.
        request(Object): request object.
        session(object): database session object.
    Returns:
        USER(object): if access_token is valid.
    Raises:
        HTTPException: If user not found.
    """
    payload: dict | None = await verify_token(access_token, request, "access")

    user = await user_service.fetch({"id": payload.get("user_id")}, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )
    return user


async def get_current_active_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Optional[User]:
    """Retrieves the current-active user using the access_token.

    Args:
        access_token(str): access_token of the user.
        request(Object): request object.
        session(object): database session object.
    Returns:
        USER(object): if access_token is valid.
    Raises:
        HTTPException: If user is not active.

    """
    user: User | None = await get_current_user(access_token, request, session)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is no longer a part of the platform.",
        )
    if user.is_suspended:
        # TODO: Add the check for suspension-duration when user model is completed.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is still suspended"
        )
    return user


async def get_current_active_superadmin(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Optional[User]:
    """Retrieves the current-active superadmin using the access_token.

    Args:
        access_token(str): access_token of the user.
        request(Object): request object.
        session(object): database session object.
    Returns:
        USER(object): if access_token is valid.
    Raises:
        HTTPException: If superadmin is not active.

    """
    user: User | None = await get_current_user(access_token, request, session)
    for role in user.roles:
        if role.name != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You have no Authorized access to this resource.",
            )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="superadmin is inactive"
        )
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="superadmin is no longer authorized",
        )
    if user.is_suspended:
        # TODO: Add the check for suspension-duration when user model is completed.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="superadmin is still suspended",
        )
    return user


async def generate_jwt_token(data: dict, token_type: str = "access") -> str:
    """Generates jwt token.

    Keyword arguments:
        data(dict): contains user_id, user_agent, user-role
        token_type(str): the token type to generate
    Return: token(str) generated
    """
    # TODO: increase the tokens ttl if remember_me is a feature.
    now = datetime.now(timezone.utc)
    if token_type == "refresh":
        expire = now + timedelta(days=Config.REFRESH_TOKEN_EXPIRY)
    elif token_type == "access":
        expire = now + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRY)
    else:
        logger.error("token type must only be access or refresh")
        raise Exception("token type must only be access or refresh")
    claims = {
        "user_id": data.get("user_id"),
        "user_agent": data.get("user_agent"),
        "sub_plan_expires_in": data.get("sub_plan_expires_in"),
        "sub_plan_id": data.get("sub_plan_id"),
        "exp": expire,
        "role": data.get("role"),
        "type": token_type,
    }

    token: str = jwt.encode(
        claims=claims, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )
    return token


async def verify_token(token: str, request: Request, token_type: str) -> Optional[dict]:
    """Verifies/Decodes jwt token.

    Args:
        token(str): token to verify
        request(Request): request object
        token_type(str): The type of token to be decoded.
    Return:
        claims(dict): the decode token.
    """
    try:
        claims: dict = jwt.decode(
            token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        decoded_token_type = claims.get("type")

        # check for token type.
        if token_type == "access":
            if decoded_token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Access Token.",
                )
        # check for token type.
        if token_type == "refresh":
            if decoded_token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Refresh Token.",
                )

        # check for token type.
        if token_type == "email_verification":
            if decoded_token_type != "email_verification":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email_verification Token.",
                )

        if token_type != "email_verification":
            request.state.current_user = claims.get("user_id")
            user_agent = request.headers.get("user-agent")
            if user_agent != claims.get("user_agent"):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return claims
    except JWTError as exc:
        logger.error(msg=f"JWTError: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalid or Expired"
        )


async def validate_superadmin_secret(input_secret: str) -> Optional[Tuple[str, bool]]:
    """
    Validates the secret used for superadmin registration.

    Args:
        input_secret(str): The secret to validate.
    Returns:
        Tuple[str, bool]: Returns a tuple with the matching secret name and True if validation is successful,
                          otherwise an empty string and False.
    """
    if not input_secret or not isinstance(input_secret, str):
        raise Exception("input_secret is missing as argument.")

    try:
        if Config.TEST == "TEST":
            test_secret = Config.TEST_SUPERADMIN_SECRET
            return "test_secret", hmac.compare_digest(input_secret, test_secret)
        secret_one: str = Config.SUPERADMIN_SECRET_ONE
        secret_two: str = Config.SUPERADMIN_SECRET_TWO
        secret_three: str = Config.SUPERADMIN_SECRET_THREE
        # Compare input secret with stored secrets securely
        if hmac.compare_digest(input_secret, secret_one):
            return "secret_one", True
        elif hmac.compare_digest(input_secret, secret_two):
            return "secret_two", True
        elif hmac.compare_digest(input_secret, secret_three):
            return "secret_three", True
        return "", False
    except Exception as exc:
        logger.error(f"validate_superadmin_secret function error: {exc}")
        raise Exception("SUPERADMIN_SECRET(s) undefined in Config.") from exc


async def check_email_deliverability(email: str):
    """
    Checks if an email address is potentially deliverable by verifying the existence of
    MX records for its domain. Caches confirmed checks to avoid unnecessary calls to
    dns-resolver server.

    Args:
        email (str): The email address to check.

    Returns:
        None: True if MX records were found.
    Raises:
        HTTPException: if MX not found
    """
    # Extract the domain from the email address
    domain = email.split("@")[1]
    # define a cache key
    domain_key = f"mx_{domain}"
    error_message = (
        "Email domain does not have valid MX records, contact your domain provider."
    )
    try:
        with get_redis_sync() as redis:
            # Check cache first
            cached_result = redis.get(domain_key)
            # return if cache is valid
            if cached_result and cached_result == "1":
                return None
            # raise exception if cache is invalid
            if cached_result == "0":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
                )

            # perform the DNS lookup asynchronously
            resolver = dns.resolver.Resolver()
            resolver.timeout = 1  # Set a timeout for the DNS query
            answers = resolver.resolve(domain, "MX")

            # Check if at least one MX record was found
            if answers:
                # Store result in cache
                redis.set(domain_key, "1", ex=3600)
                # return
                return None
            logger.info(f"Domain not found or no answer for DNS query:  {domain}")
            # Cache failed result
            redis.set(domain_key, "0", ex=3600)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message,
            )

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as exc:
        logger.error(
            f"Domain not found or no answer for DNS query:  {domain}: error: {exc}",
            exc_info=True,
        )
        # Cache failed result
        redis.set(domain_key, "0", ex=3600)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        ) from exc


async def generate_email_verification_token(
    email: str, token_type: str = "email_verification"
) -> str:
    """Generates token for email verification.

    Keyword arguments:
        email(str): the email of the user to encode in the token.
        token_type(str): the token type to generate
    Return: token(str) generated
    """
    # TODO: increase the tokens ttl if remember_me is a feature.
    now = datetime.now(timezone.utc)
    if token_type != "email_verification":
        raise Exception("token type must only be email_verification")
    claims = {
        "email": email,
        "exp": now + timedelta(minutes=5),
        "type": token_type,
    }

    token: str = jwt.encode(
        claims=claims, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )
    return token


async def check_user_suspension_status(
    data: dict, session: AsyncSession
) -> Optional[User]:
    """
    Checks if user is suspended, inactive, or deleted.

    Args:
        data(dict): the user data, e.g {"id": "12345-252463647-7544447-432624657"}.
        session(AsyncSession): database session object.
    Returns:
        User if cleared.
    Raises:
        HTTPException if suspended, inactive, or deleted.
    """
    user_to_verify = await user_service.fetch(data, session)
    if not user_to_verify:
        return
    if not user_to_verify.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )
    if user_to_verify.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is no longer a part of the platform.",
        )
    if user_to_verify.is_suspended:
        # TODO: Add the check for suspension-duration when user model is completed.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is still suspended"
        )
    return user_to_verify


async def authenticate_user(
    request: Request,
    access_token: str,
) -> Optional[dict]:
    """
    Authenticates a user and verifies their role.

    Args:
        request(Request): request object.
        access_token(str): token to decode
    Returns:
        claims(dict): the decoded token.
    """

    claims = await verify_token(
        token=access_token, request=request, token_type="access"
    )
    claim_role = claims.get("role")
    if not claim_role:
        raise HTTPException(status_code=401, detail="Access denied.")

    return claims


async def verify_premium_user_access_token(
    request: Request, access_token: str, session: AsyncSession
) -> Optional[dict]:
    """
    Verifies a premium user, verifies if the plan has expired, and verifies their role.

    Args:
        request(Request): request object.
        access_token(str): token to decode.
        session(AsyncSession): database session object.
    Returns:
        claims(dict): the decoded token.
    """

    claims = await verify_token(
        token=access_token, request=request, token_type="access"
    )

    premium_expires_in = datetime.strptime(
        claims.get("sub_plan_expires_in"), "%Y/%m/%d %H:%M:%S"
    )
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.id == claims.get("sub_plan_id")
    )
    result = await session.execute(stmt)
    sub_plan = result.scalar_one_or_none()
    if not sub_plan:
        raise HTTPException(status_code=400, detail="User has no subscription plan.")
    if sub_plan.name == "free_tier":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="User is on a free tier plan.",
        )
    if premium_expires_in < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription has expired.",
        )

    return claims


async def authenticate_superadmin(
    request: Request,
    access_token: str,
) -> Optional[dict]:
    """
    Authenticates a superadmin and verifies their role.

    Args:
        request(Request): request object.
        access_token(str): token to decode
    Returns:
        claims(dict): the decoded token.
    """

    claims = await verify_token(
        token=access_token, request=request, token_type="access"
    )
    claim_role = claims.get("role")
    if claim_role != "superadmin" and claim_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have enough permission to perform this action.",
        )

    return claims


async def authenticate_premium_user(
    user_id: str, session: AsyncSession
) -> Optional[SubscriptionPlan]:
    """
    Aunthenticates a premium user.

    Args.
        user_id(str): The user to authenticate.
        session(AsyncSession): database async session object.
    Returns:
        SubscriptionPlan(object): if subscribed.
    Raises:
        401 status code if on free tier plan. or subscription expired.
    """
    sub_stmt = select(Subscription).where(Subscription.subscriber_id == user_id)

    result = await session.execute(sub_stmt)
    subscribed = result.scalar_one_or_none()
    if subscribed.expires_in < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription has expired.",
        )
    stmt = (
        select(SubscriptionPlan)
        .join(Subscription, Subscription.subscription_plan_id == SubscriptionPlan.id)
        .join(User, User.id == Subscription.subscriber_id)
        .where(User.id == user_id)
    )
    result = await session.execute(stmt)
    subscription_plan = result.scalar_one_or_none()
    if subscription_plan.name not in ["weekly", "monthly", "yearly"]:
        raise HTTPException(status_code=401, detail="User is on a free tier plan.")
    return subscription_plan
