import pytest

from api.v1.user.service import user_service
from api.v1.profile.service import (
    profile_service,
    profile_preference_service,
    profile_traits_service,
)


class TestProfileService:
    """
    Tests class for profile service.
    """

    @pytest.mark.asyncio
    async def test_create_user(
        self, mock_jayson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for creating profile.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        # create profile
        jayson_profile = await profile_service.create(
            {"recovery_email": "jayson@gmail.com", "user_id": jayson_user.id},
            test_get_session,
        )

        # create profile preference
        jayson_profile_pref = await profile_preference_service.create(
            {"joining_purpose": "friendship", "profile_id": jayson_profile.id},
            test_get_session,
        )

        # create profile traits
        jayson_profile_trait = await profile_traits_service.create(
            {"hobbies": {"dancing": "dancing"}, "profile_id": jayson_profile.id},
            test_get_session,
        )

        # assertions
        assert jayson_profile is not None
        assert jayson_profile_pref is not None
        assert jayson_profile_trait is not None
        assert jayson_profile_trait.hobbies == {"dancing": "dancing"}
