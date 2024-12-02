from typing import Optional, Dict
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime, timezone

from api.v1.auth.dependencies import (
    check_idempotency_key,
    generate_idempotency_key,
    generate_jwt_token,
    check_email_deliverability,
    generate_email_verification_token,
    verify_token,
    check_user_suspension_status,
)
from api.v1.auth.schema import (
    RegisterOutputSchema,
    UserProfileSchema,
    UserLoginSchema,
    LoginOutputSchema,
    LoginShema,
    UserCreate,
    ResendVerificationOutputSchema,
    EmailVerificationOutputSchema,
    AccessToken
)
from api.v1.user.service import user_service
from api.v1.profile.service import (
    profile_service,
    profile_preference_service,
    profile_traits_service,
)
from api.v1.user.schema import UserBase
from api.v1.profile.schema import ProfileBase
from api.utils.task_logger import create_logger
from api.utils.celery_setup.tasks import send_email
from api.utils.settings import Config
from api.database.redis_database import get_redis_sync
from api.v1.role_and_permission.service import role_service, user_roles_service
from api.v1.subscriptions.service import subscription_service, subscription_plan_service
from api.v1.two_fa.service import two_factor_service
from api.v1.trusted_devices.service import trusted_device_service


logger = create_logger("Authentication Service")


class AuthService:
    """
    Authentication service class.
    """

    async def authenticate(
        self, schema: LoginShema, session: AsyncSession, request: Request
    ) -> Optional[LoginOutputSchema]:
        """
        Logs in a user.

        Args:
            schema(object): pydantic model.
            session(asyncsession): database async session object.
            request(Request): request object.
        Returns:
            LoginOutputSchema(object): contains user data, tokens, and success message if successful
        """
        async with session.begin().session as session:
            await check_email_deliverability(
                schema.email
            )  # raises 400 if deliverability fails
            # check if email exists
            user_exists = await check_user_suspension_status(
                {"email": schema.email}, session
            )

            # raise exception if user not found
            if not user_exists:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            # compare password if email exists
            is_passsword_valid = user_exists.verify_password(schema.password)
            if not is_passsword_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            # raise exception if email is not verified.
            if not user_exists.email_verified:
                msg_one = (
                    "Email not verified, check your inbox or spam. If link has expired,"
                )
                msg_two = (
                    " request for another link with the email used for registration"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"{msg_one}{msg_two}",
                )

            # TODO: check if user is logging in from a new device using the device_token_id
            # notify the user via email about logging in from a new device

            # Check if user has 2FA enabled
            if user_exists.two_factor_enabled:
            # Check if device is trusted
                is_trusted = await trusted_device_service.verify_device_trust(
                    user_exists.id, 
                    schema.device_info, 
                    session
                )
                
                if is_trusted:
                    # Skip 2FA and generate tokens directly
                    return await self.generate_tokens_and_response(request, user_exists, session)
                
                # Generate temporary token for 2FA verification
                temp_token = await two_factor_service.create_temp_token(user_exists.id)
                return LoginOutputSchema(
                    requires_2fa=True,
                    temp_token=temp_token,
                    message="2FA verification required",
                )
    
            # Regular login flow for non-2FA users
            return await self.generate_tokens_and_response(request, user_exists, session)

    async def generate_tokens_and_response(
        self,
        request: Request,
        user,
        session: AsyncSession
    ) -> Optional[LoginOutputSchema]:
        """Generates tokens and API response for authenticated users"""

        user_base = UserBase(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                email_verified=user.email_verified,
                is_suspended=user.is_suspended,
                is_deleted=user.is_deleted,
                roles=[role.name for role in user.roles],
            )

        profile = await profile_service.fetch({"user_id": user.id}, session)
        profile_base = ProfileBase.model_validate(profile, from_attributes=True)

        # generate tokens
        # TODO: increase the tokens ttl if remember_me is a feature.

        # TODO: Add user subscription to token to encode.
        subscription = await subscription_service.fetch(
            {"subscriber_id": user.id}, session
        )
        expires_in = subscription.expires_in.strftime("%Y/%m/%d %H:%M:%S")
        access_token = await generate_jwt_token(
            {
                "user_id": user.id,
                "user_agent": request.headers.get("user-agent"),
                "role": user.roles[0].name,
                "sub_plan_expires_in": expires_in,
                "sub_plan_id": subscription.subscription_plan_id,
            }
        )
        refresh_token = await generate_jwt_token(
            {
                "user_id": user.id,
                "user_agent": request.headers.get("user-agent"),
                "role": user.roles[0].name,
                "sub_plan_expires_in": expires_in,
                "sub_plan_id": subscription.subscription_plan_id,
            },
            "refresh",
        )

        user_login_schema = UserLoginSchema(
            profile=profile_base,
            user=user_base,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        # set current_user for loggin purposes.
        request.state.current_user = user.id

        return LoginOutputSchema(data=user_login_schema)

    async def register_regular_user(
        self, user_data: UserCreate, session: AsyncSession
    ) -> Optional[RegisterOutputSchema]:
        """
        Create a new user, hash password, and store in the database.
        Enforces password matching and idempotency by checking if the user already exists.

        :param user_data: Data for user creation (email, password, confirm_password)
        :param session: AsyncSession for database transactions
        :return: Success message in case of successful user creation
        """
        async with session.begin().session as session:
            await check_email_deliverability(user_data.email)

            user_registered = await check_idempotency_key(user_data.email, session)

            if user_registered:
                user_base = UserBase(
                    id=user_registered.id,
                    email=user_registered.email,
                    first_name=user_registered.first_name,
                    last_name=user_registered.last_name,
                    created_at=user_registered.created_at,
                    updated_at=user_registered.updated_at,
                    email_verified=user_registered.email_verified,
                    is_suspended=user_registered.is_suspended,
                    is_deleted=user_registered.is_deleted,
                    roles=[role.name for role in user_registered.roles],
                )
                profile = await profile_service.fetch(
                    {"user_id": user_registered.id}, session=session
                )
                profile_base = ProfileBase.model_validate(profile, from_attributes=True)
                user_profile = UserProfileSchema(user=user_base, profile=profile_base)
                return RegisterOutputSchema(
                    data=user_profile, message="User Already Registered."
                )

            # Check if the email is already registered
            existing_user = await user_service.fetch(
                {"email": user_data.email}, session
            )
            if existing_user:
                logger.warning(
                    "Duplicate registration attempt for email: %s", user_data.email
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use..",
                )

            payload: dict = user_data.model_dump(exclude={"confirm_password"})
            payload["idempotency_key"] = await generate_idempotency_key(
                payload.get("email")
            )
            # Create new user instance
            new_user = await user_service.create(payload, session)

            new_user_profile = await profile_service.create(
                {"user_id": new_user.id}, session
            )
            _ = await profile_traits_service.create(
                {"profile_id": new_user_profile.id}, session
            )
            _ = await profile_preference_service.create(
                {"profile_id": new_user_profile.id}, session
            )
            # Add a free_tier subscription to user on registration.
            free_tier_plan = await subscription_plan_service.fetch(
                {"name": "free_tier"}, session
            )
            _ = await subscription_service.create(
                {
                    "subscriber_id": new_user.id,
                    "subscription_plan_id": free_tier_plan.id,
                    "status": "active",
                    "expires_in": datetime.now(timezone.utc) + timedelta(weeks=100000),
                },
                session,
            )

            if not Config.TEST:
                # generate token
                token = await generate_email_verification_token(user_data.email)

                context = {
                    "recepient_email": user_data.email,
                    "link": f"http://127.0.0.1:7001/api/v1/auth/verify-email?token={token}",
                    "subject": "Email Verification",
                    "template_name": "email-verification.html",
                }

                # send token to email using background service
                _ = send_email.delay(context)

            role = await role_service.fetch({"name": "user"}, session)

            await user_roles_service.insert_if_not_exists(
                session=session, user_id=new_user.id, role_id=role.id
            )

            user_base = UserBase(
                id=new_user.id,
                email=new_user.email,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                created_at=new_user.created_at,
                updated_at=new_user.updated_at,
                email_verified=new_user.email_verified,
                is_suspended=new_user.is_suspended,
                is_deleted=new_user.is_deleted,
                roles=[role.name],
            )
            profile_base = ProfileBase.model_validate(
                new_user_profile, from_attributes=True
            )
            user_profile = UserProfileSchema(user=user_base, profile=profile_base)

            return RegisterOutputSchema(data=user_profile)

    async def resend_verification_email(
        self, email: str, session: AsyncSession
    ) -> Optional[ResendVerificationOutputSchema]:
        """
        Generates and sends email verification token.

        Args:
            email(str): The email to resend verification to.
        Returns:
            ResendVerificationOutputSchema(pydantic model): as response
        """

        user_to_verify = await check_user_suspension_status({"email": email}, session)
        if not user_to_verify:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
            )
        if user_to_verify.email_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already verified"
            )

        # generate token
        token = await generate_email_verification_token(email)

        context = {
            "recepient_email": email,
            "link": f"http://127.0.0.1:7001/api/v1/auth/verify-email?token={token}",
            "subject": "Email Verification",
            "template_name": "email-verification.html",
        }

        # send token to email using background service
        _ = send_email.delay(context)

        return ResendVerificationOutputSchema()

    async def verify_email(
        self, token: str, session: AsyncSession, request: Request
    ) -> Optional[EmailVerificationOutputSchema]:
        """
        Verifies user email encoded in the token.

        Args:
            token(str): The token to decode and use for verification.
            session(AsyncSession): database async session object.
            request(Request): the request object.
        Returns:
            ResendVerificationOutputSchema(pydantic model): as response
        """
        claims = await verify_token(token, request, "email_verification")
        async with session.begin().session as session:

            user_to_verify = await check_user_suspension_status(
                {"email": claims.get("email")}, session
            )
            if not user_to_verify:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
                )
            if user_to_verify.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already verified",
                )
            user_to_verify.email_verified = True
            await session.commit()

            return EmailVerificationOutputSchema()

    async def logout_user(self, access_token: str, refresh_token: str) -> Dict:
        """
        Logs out the user by blacklisting the access and refresh tokens.

        Args:
            access_token (str): The access token to blacklist.
            refresh_token (str): The refresh token to blacklist.
        Returns:
            Dict: A success message indicating the logout status.
        """
        try:
            with get_redis_sync() as redis:
                redis.setex(
                    f"blacklist:access_token:{access_token}",
                    timedelta(hours=1),
                    "blacklisted",
                )
                redis.setex(
                    f"blacklist:refresh_token:{refresh_token}",
                    timedelta(days=7),
                    "blacklisted",
                )

                logger.info(
                    f"User logged out, tokens blacklisted. Access: {access_token}, Refresh: {refresh_token}"
                )

                return {"status_code": 200, "message": "Logout successful", "data": {}}

        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Logout failed. Please try again later."
            )

    async def oauth2_authenticate(
        self, email: str, password: str, session: AsyncSession, request: Request
    ):
        """
        Authenticates a user for the openapi docs usage.
        """
        # retrieve the user using email
        user = await check_user_suspension_status({"email": email}, session)
        # if no user with provided details is found
        if not user:
            # raise an exception
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
        # raise exception if email is not verified.
        if not user.email_verified:
            msg_one = (
                "Email not verified, check your inbox or spam. If link has expired,"
            )
            msg_two = " request for another link with the email used for registration"
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{msg_one}{msg_two}",
            )

        # check if the user provided the right password
        password_valid = user.verify_password(password)
        # check if password is correct
        if not password_valid:
            # raise an exception if there is a password mismatch
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )

        # generate access token
        subscription = await subscription_service.fetch(
            {"subscriber_id": user.id}, session
        )

        expires_in = subscription.expires_in.strftime("%Y/%m/%d %H:%M:%S")

        data = {
            "user_id": user.id,
            "role": user.roles[0].name,
            "user_agent": request.headers.get("user-agent"),
            "sub_plan_expires_in": expires_in,
            "sub_plan_id": subscription.subscription_plan_id,
        }
        access_token = await generate_jwt_token(data)
        # return access token
        return AccessToken(access_token=access_token)


auth_service = AuthService()
