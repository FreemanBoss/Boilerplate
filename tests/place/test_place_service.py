import pytest
from datetime import time

from api.v1.user.service import user_service
from api.v1.place.service import place_service, place_category_service


class TestPlaceService:
    """
    Tests class for place service.
    """

    @pytest.mark.asyncio
    async def test_create_place(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for creating place.
        """
        mock_johnson_user_dict.pop("confirm_password")
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        restaurant = await place_category_service.create(
            {"name": "Restaurant"}, test_get_session
        )

        new_place = await place_service.create(
            {
                "category_id": restaurant.id,
                "creator_id": johnson_user.id,
                "name": "some name",
                "banner": {"banner_one": "some banner"},
                "about": "all good",
            },
            test_get_session,
        )

        assert new_place is not None
        assert new_place.opening_hour == time(9, 0, 0)

    @pytest.mark.asyncio
    async def test_update_place(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for update place.
        """
        mock_johnson_user_dict.pop("confirm_password")
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        restaurant = await place_category_service.create(
            {"name": "Restaurant"}, test_get_session
        )

        new_place = await place_service.create(
            {
                "category_id": restaurant.id,
                "creator_id": johnson_user.id,
                "name": "some name",
                "banner": {"banner_one": "some banner"},
                "about": "all good",
            },
            test_get_session,
        )

        assert new_place is not None

        updated_new_place = await place_service.update(
            [
                {"creator_id": johnson_user.id, "name": "some name"},
                {"name": "no name"},
            ],
            test_get_session,
        )

        assert updated_new_place.name == "no name"
