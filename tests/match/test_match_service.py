import pytest

from api.v1.user.service import user_service
from api.v1.match.service import match_service


class TestMatchService:
    """
    Tests class for match service.
    """
    @pytest.mark.asyncio
    async def test_create_a_match(self,
                               mock_johnson_user_dict,
                               mock_jayson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for creating match.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        jayson_user = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        
        new_match = await match_service.create(
            {
                "user_sent_match_id": johnson_user.id,
                "user_accept_match_id": jayson_user.id,
                "notify": False
            },
            session=test_get_session
        )
        assert new_match is not None

    @pytest.mark.asyncio
    async def test_update_a_match(self,
                               mock_johnson_user_dict,
                               mock_jayson_user_dict,
                               test_get_session,
                               test_setup):
        """
        Tests for update match.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")
        
        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        jayson_user = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        
        new_match = await match_service.create(
            {
                "user_sent_match_id": johnson_user.id,
                "user_accept_match_id": jayson_user.id,
                "notify": False
            },
            session=test_get_session
        )
        assert new_match is not None
        
        updated_match = await match_service.update(
            [
                {
                   "user_sent_match_id": johnson_user.id,
                    "user_accept_match_id": jayson_user.id,
                    "notify": False
                },
                {
                    "notify": True,
                }
            ],
            session=test_get_session
        )
        
        assert updated_match.notify is True
