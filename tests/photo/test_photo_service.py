import pytest

from api.v1.user.service import user_service
from api.v1.photo.service import photo_service


class TestPhotoService:
    """
    Tests class for photo service.
    """
    @pytest.mark.asyncio
    async def test_create_a_photo(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for create photo.
        """
        mock_johnson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        
        new_photo = await photo_service.create(
            {
                "user_id": johnson_user.id,
                "linked_to": "profile",
                "url": "some url",
                "is_profile_picture": True
            },
            test_get_session
        )
        
        assert new_photo is not None

    @pytest.mark.asyncio
    async def test_update_a_photo(self,
                               mock_johnson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for update photo.
        """
        mock_johnson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        
        new_photo = await photo_service.create(
            {
                "user_id": johnson_user.id,
                "linked_to": "profile",
                "url": "some url",
                "is_profile_picture": True
            },
            test_get_session
        )
        
        assert new_photo is not None
        assert new_photo.url == "some url"
        
        updated_photo = await photo_service.update(
            [
                {
                    "user_id": johnson_user.id,
                    "linked_to": "profile",
                    "is_profile_picture": True
                },
                {
                    "url": "new url"
                }
            ],
            test_get_session
        )
        
        assert updated_photo.url == "new url"
