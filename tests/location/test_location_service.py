import pytest

from api.v1.user.service import user_service
from api.v1.location.service import location_service


class TestLocationService:
    """
    Tests class for location service.
    """

    @pytest.mark.asyncio
    async def test_create_a_location(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for create location.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        location_name = {"country": "Nigeria", "state": "Abuja", "city": "Abuja"}

        new_location = await location_service.create(location_name, test_get_session)

        assert new_location.city == location_name["city"]

    @pytest.mark.asyncio
    async def test_update_a_location(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for update location.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        location_name = {"country": "Nigeria", "state": "Abuja", "city": "Abuja"}
        location_two = {"country": "Nigeria", "state": "Lagos", "city": "Lagos"}

        new_location = await location_service.create(location_name, test_get_session)

        assert new_location.state == location_name["state"]

        updated_location = await location_service.update(
            [location_name, location_two], test_get_session
        )
        assert updated_location.city == location_two["city"]
        assert updated_location.state == location_two["state"]
        assert updated_location.country == location_two["country"]
