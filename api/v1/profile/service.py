from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.base.services import Service
from api.v1.profile.model import Profile, ProfilePreference, ProfileTrait
from api.v1.user.model import User
from api.v1.profile.schema import (
    ProfileUpdateRequest,
    ProfileBase,
    ProfileUpdateResponse,
    ProfileUpdateSchema,
    UpdateProfileBase,
    UpdateResponseSchema,
    ProfileUpdateSchema,
    FetchProfileResponseSchema,
    DeleteUserResponse,
)
from api.v1.location.service import user_location_service
from api.v1.auth.dependencies import authenticate_user
from api.v1.user.service import user_service


class ProfileService(Service):
    """
    Service class for profile.
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)

    async def update_profile(
        self, schema: ProfileUpdateRequest, session: AsyncSession, user: User
    ) -> Optional[ProfileUpdateResponse]:
        """
        Updates a users profile.

        Args:
            schema(object): pydantic model.
            session(asyncsession): database async session object.
            user(User): the current authenticated user.
        Returns:
            ProfileUpdateResponse(object): contains profile data and success message if successful
        """
        async with session.begin().session as session:

            profile = await self.fetch({"user_id": user.id}, session=session)

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found",
                )

            profile_data = schema.model_dump(exclude_unset=True)

            where = [{"profile_id": profile.id}, profile_data]

            # update the profile preferences
            await profile_preference_service.update(where, session)

            # update the profile traits
            await profile_traits_service.update(where, session)

            where = [{"id": profile.id}, profile_data]

            # update the profile
            updated_profile = await self.update(where, session)

            # profile = await profile_service.fetch({"user_id": user_exists.id}, session)
            profile_base = ProfileBase.model_validate(updated_profile)

            return ProfileUpdateResponse(
                message="Profile successfully updated.", data=profile_base
            )

    async def update_profile_fields(
        self,
        schema: ProfileUpdateSchema,
        session: AsyncSession,
        profile_id: str,
        user_id: str,
    ) -> Optional[UpdateResponseSchema]:
        """
        Updates a user profile individual field.

        Args:
            schema(object): pydantic model.
            session(asyncsession): database async session object.
            profile_id(str): the current authenticated profile_id.
            user_id(str): the current authenticated user_id.
        Returns:
            UpdateResponseSchema(object): contains profile data and success message if successful
        """
        profile_to_update = await self.fetch(
            {"user_id": user_id, "id": profile_id}, session
        )
        if not profile_to_update:
            raise HTTPException(status_code=400, detail="Profile not found")
        profile_preference = await profile_preference_service.fetch(
            {"profile_id": profile_id}, session
        )
        profile_traits = await profile_traits_service.fetch(
            {"profile_id": profile_to_update.id}, session
        )

        if schema.bio:
            _ = await self.update([{"id": profile_id}, {"bio": schema.bio}], session)

        if schema.family_plans:
            profile_preference.family_plans = schema.family_plans

        if schema.lifestyle_habits:
            profile_preference.lifestyle_habits = schema.lifestyle_habits

        if schema.political_view:
            profile_preference.political_view = schema.political_view

        if schema.religion:
            profile_preference.religion = schema.religion

        if schema.genotype:
            profile_preference.genotype = schema.genotype
            await session.commit()

        if schema.hobbies:
            profile_traits.hobbies = schema.hobbies

        await session.commit()

        location = await user_location_service.get_current_location(
            user_id=user_id, session=session
        )

        profile_base = UpdateProfileBase(
            id=profile_to_update.id,
            user_id=user_id,
            recovery_email=profile_to_update.recovery_email,
            date_of_birth=profile_to_update.date_of_birth,
            verified=profile_to_update.verified,
            phone=profile_to_update.phone,
            bio=profile_to_update.bio,
            height=profile_to_update.height,
            genotype=profile_to_update.genotype,
            last_active_at=profile_to_update.last_active_at,
            location={
                "city": location.city,
                "state": location.state,
                "country": location.country,
            },
            created_at=profile_to_update.created_at,
            updated_at=profile_to_update.updated_at,
            gender=profile_to_update.gender,
            joining_purpose=profile_preference.joining_purpose,
            preferred_gender=profile_preference.preferred_gender,
            desired_relationship=profile_preference.desired_relationship,
            ideal_partner_qualities=profile_preference.ideal_partner_qualities,
            location_preference=profile_preference.location_preference,
            age_range=(
                profile_preference.age_range[0] if profile_preference.age_range else ""
            ),
            distance_range=profile_preference.distance_range,
            hobbies=profile_traits.hobbies,
            lifestyle_habits=profile_preference.lifestyle_habits,
            family_plans=profile_preference.family_plans,
            religion=profile_preference.religion,
            political_view=profile_preference.political_views,
        )

        return UpdateResponseSchema(data=profile_base)

    async def fetch_profile(
        self, session: AsyncSession, profile_id: str, user_id: str
    ) -> Optional[FetchProfileResponseSchema]:
        """
        Retrieves a user profile.

        Args:
            schema(object): pydantic model.
            session(asyncsession): database async session object.
            profile_id(str): the current authenticated profile_id.
            user_id(str): the current authenticated user_id.
        Returns:
            FetchProfileResponseSchema(pydantic): contains profile data and success message if successful
        """
        profile_exists = await self.fetch(
            {"id": profile_id, "user_id": user_id}, session
        )

        if not profile_exists:
            raise HTTPException(status_code=400, detail="Profile not found.")
        profile_traits = await profile_traits_service.fetch(
            {"profile_id": profile_exists.id}, session
        )

        profile_preference = await profile_preference_service.fetch(
            {"profile_id": profile_exists.id}, session
        )
        location = await user_location_service.get_current_location(
            user_id=user_id, session=session
        )

        profile_base = UpdateProfileBase(
            id=profile_exists.id,
            user_id=user_id,
            recovery_email=profile_exists.recovery_email,
            date_of_birth=profile_exists.date_of_birth,
            verified=profile_exists.verified,
            phone=profile_exists.phone,
            bio=profile_exists.bio,
            height=profile_exists.height,
            genotype=profile_exists.genotype,
            last_active_at=profile_exists.last_active_at,
            location={
                "city": location.city,
                "state": location.state,
                "country": location.country,
            },
            created_at=profile_exists.created_at,
            updated_at=profile_exists.updated_at,
            gender=profile_exists.gender,
            joining_purpose=profile_preference.joining_purpose,
            preferred_gender=profile_preference.preferred_gender,
            desired_relationship=profile_preference.desired_relationship,
            ideal_partner_qualities=profile_preference.ideal_partner_qualities,
            location_preference=profile_preference.location_preference,
            age_range=(
                profile_preference.age_range[0] if profile_preference.age_range else ""
            ),
            distance_range=profile_preference.distance_range,
            hobbies=profile_traits.hobbies,
            lifestyle_habits=profile_preference.lifestyle_habits,
            family_plans=profile_preference.family_plans,
            religion=profile_preference.religion,
            political_view=profile_preference.political_views,
        )

        return FetchProfileResponseSchema(data=profile_base)

    async def soft_delete_user(
        self,
        session: AsyncSession,
        current_user: User,
    ) -> Optional[DeleteUserResponse]:
        """
        Soft delete a user
        Returns:
            DeleteUserResponse(object): contains success message if successful
        """

        async with session.begin().session as session:

            # update the user
            where = [{"user_id": current_user.id}, {"is_deleted": True}]
            updated_user = await user_service.update(where, session)

            if updated_user.is_deleted:
                return DeleteUserResponse

            return DeleteUserResponse(status_code=500, message="User delete failed")


class ProfilePreferenceService(Service):
    """
    Service class for profile preference.
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


class ProfileTraitService(Service):
    """
    Service class for profile traits.
    """

    def __init__(self, model) -> None:
        """
        Constructor.
        """
        super().__init__(model)


profile_service = ProfileService(Profile)
profile_preference_service = ProfilePreferenceService(ProfilePreference)
profile_traits_service = ProfileTraitService(ProfileTrait)
