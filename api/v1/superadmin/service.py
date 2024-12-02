from typing import Optional
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.v1.auth.dependencies import (
    validate_superadmin_secret,
    check_idempotency_key,
    generate_idempotency_key,
    check_email_deliverability,
    generate_email_verification_token,
    check_user_suspension_status,
)
from api.v1.auth.schema import (
    RegisterSuperadminSchema,
    RegisterOutputSchema,
    UserProfileSchema,
)
from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.user.schema import UserBase
from api.v1.profile.schema import ProfileBase
from api.utils.task_logger import create_logger
from api.utils.celery_setup.tasks import send_email
from api.utils.settings import Config
from api.v1.role_and_permission.service import role_service, user_roles_service


logger = create_logger("Authentication Service")


class SuperAdminService:
    """
    Authentication service class.
    """

    async def register(
        self, schema: RegisterSuperadminSchema, session: AsyncSession, request: Request
    ) -> Optional[RegisterOutputSchema]:
        """
        Registers a superadmin.

        Args:
            schema(object): pydantic model.
            session(asyncsession): database async session object.
            request(Request): request object.
        Returns:
            RegisterOutputSchema
        """
        async with session.begin().session as session:
            await check_email_deliverability(
                schema.email
            )  # raises 400 if deliverability fails
            secret_name, is_secret_valid = await validate_superadmin_secret(
                schema.secret_token
            )
            if not is_secret_valid:
                raise HTTPException(status_code=400, detail="Invalid secret.")
            user_registered = await check_idempotency_key(schema.email, session)

            if user_registered:
                roles = [role.name for role in user_registered.roles]
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
                    roles=roles,
                )
                profile = await profile_service.fetch(
                    {"user_id": user_registered.id}, session=session
                )
                profile_base = ProfileBase.model_validate(profile, from_attributes=True)
                user_profile = UserProfileSchema(user=user_base, profile=profile_base)
                message = "Superadmin Already Registered."
                if "superadmin" not in roles:
                    message = "User Already Registered, but not as a superadmin."
                return RegisterOutputSchema(data=user_profile, message=message)
            user_email_exists = await user_service.fetch(
                {"email": schema.email}, session
            )
            if user_email_exists:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="email already in use.",
                )
            payload: dict = schema.model_dump(
                exclude={"confirm_password", "secret_token"}
            )
            payload["idempotency_key"] = await generate_idempotency_key(
                payload.get("email")
            )
            payload["secret_token_identifier"] = secret_name
            # TODO: Include the retrieval of device_token_id when collaboration with mobile devs commences.

            new_superadmin = await user_service.create(payload, session)

            new_superadmin_profile = await profile_service.create(
                {"user_id": new_superadmin.id}, session
            )

            role = await role_service.fetch({"name": "superadmin"}, session)

            _ = await user_roles_service.insert_if_not_exists(
                session=session, role_id=role.id, user_id=new_superadmin.id
            )
            if not Config.TEST:
                # generate token
                token = await generate_email_verification_token(schema.email)

                context = {
                    "recepient_email": schema.email,
                    "link": f"http://127.0.0.1:7001/api/v1/auth/verify-email?token={token}",
                    "subject": "Email Verification",
                    "template_name": "email-verification.html",
                }

                # send token to email using background service
                _ = send_email.delay(context)

            user_base = UserBase(
                id=new_superadmin.id,
                email=new_superadmin.email,
                first_name=new_superadmin.first_name,
                last_name=new_superadmin.last_name,
                created_at=new_superadmin.created_at,
                updated_at=new_superadmin.updated_at,
                email_verified=new_superadmin.email_verified,
                is_suspended=new_superadmin.is_suspended,
                is_deleted=new_superadmin.is_deleted,
                roles=[role.name],
            )
            profile_base = ProfileBase.model_validate(
                new_superadmin_profile, from_attributes=True
            )
            user_profile = UserProfileSchema(user=user_base, profile=profile_base)

            return RegisterOutputSchema(data=user_profile)

    async def register_users(
        self, data: dict, session: AsyncSession, secret_token_identifier: str
    ) -> Optional[RegisterOutputSchema]:
        """
        Create a new user, hash password, and store in the database.
        Enforces password matching and idempotency by checking if the user already exists.

        :param data: Data for user creation (email, password, confirm_password)
        :param session: AsyncSession for database transactions
        :return: Success message in case of successful user creation
        """
        async with session.begin().session as session:
            email = data.get("email", "")
            role = data.pop("role", "")

            role_exists = await role_service.fetch({"name": role}, session)
            if not role_exists:
                raise HTTPException(
                    status_code=400,
                    detail="Role does not exist, create a new role and try again.",
                )
            await check_email_deliverability(email)

            user_registered = await check_idempotency_key(email, session)

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
                    roles=[role_exists.name],
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
            existing_user = await check_user_suspension_status(
                {"email": email}, session
            )
            if existing_user:
                logger.warning(f"Duplicate registration attempt for email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use..",
                )

            data["idempotency_key"] = await generate_idempotency_key(email)
            data["secret_token_identifier"] = secret_token_identifier
            # Create new user instance
            new_user = await user_service.create(data, session)

            new_user_profile = await profile_service.create(
                {"user_id": new_user.id}, session
            )

            _ = user_roles_service.insert_if_not_exists(
                role_id=role_exists.id, user_id=new_user.id, session=session
            )

            if not Config.TEST:
                # generate token
                token = await generate_email_verification_token(email)

                context = {
                    "recipient_email": email,
                    "link": f"http://127.0.0.1:7001/api/v1/auth/verify-email?token={token}",
                    "subject": "Email Verification",
                    "template_name": "email-verification.html",
                    "first_name": "Dear",
                }

                # send token to email using background service
                _ = send_email.delay(context)

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
                roles=[role_exists.name],
            )
            profile_base = ProfileBase.model_validate(
                new_user_profile, from_attributes=True
            )
            user_profile = UserProfileSchema(user=user_base, profile=profile_base)

            return RegisterOutputSchema(data=user_profile)


superadmin_service = SuperAdminService()
