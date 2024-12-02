from tests.conftest_helper import create_login_payload
import pytest

from tests.sticker.conftest_helper import create_sticker_helper


class TestStickerRoute:
    """
    Test class for Sticker route.
    """

    @pytest.mark.asyncio
    async def test_fetch_a_sticker(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful sticker retrieval.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        (
            new_sticker_one,
            new_sticker_two,
            exchanged_sticker_one,
            exchanged_sticker_two,
        ) = await create_sticker_helper(
            test_get_session, johnson_superadmin.id, jayson_user.id
        )
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url=f"/api/v1/stickers/{new_sticker_one.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Sticker retrieved successfully."
        assert data["data"]["id"] == new_sticker_one.id

    @pytest.mark.asyncio
    async def test_fetch_a_notexisting_sticker(self, client, test_setup, mock_creation):
        """
        Test for successful validation of not-existing sticker.
        """
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/stickers/fake_id",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        data = response.json()

        assert data["message"] == "sticker not found"
        assert data["data"] == {}

    @pytest.mark.asyncio
    async def test_fetch_user_received_stickers(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user received sticker retrieval.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        (
            new_sticker_one,
            new_sticker_two,
            exchanged_sticker_one,
            exchanged_sticker_two,
        ) = await create_sticker_helper(
            test_get_session, johnson_superadmin.id, jayson_user.id
        )
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/stickers?received=true",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Received stickers retrieved successfully."
        assert data["data"][0]["id"] == new_sticker_one.id
        assert data["data"][0]["name"] == new_sticker_one.name
        assert data["data"][0]["price"] == new_sticker_one.price
        assert data["data"][0]["url"] == new_sticker_one.url
        assert data["data"][0]["total_quantity"] == 23

    @pytest.mark.asyncio
    async def test_fetch_user_sent_stickers(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user sent sticker retrieval.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        (
            new_sticker_one,
            new_sticker_two,
            exchanged_sticker_one,
            exchanged_sticker_two,
        ) = await create_sticker_helper(
            test_get_session, johnson_superadmin.id, jayson_user.id
        )
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/stickers?sent=true",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Sent stickers retrieved successfully."
        assert data["data"][0]["id"] == new_sticker_two.id
        assert data["data"][0]["name"] == new_sticker_two.name
        assert data["data"][0]["price"] == new_sticker_two.price
        assert data["data"][0]["url"] == new_sticker_two.url
        assert data["data"][0]["total_quantity"] == 12

    @pytest.mark.asyncio
    async def test_fetch_query_params_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful query params validations.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        (
            new_sticker_one,
            new_sticker_two,
            exchanged_sticker_one,
            exchanged_sticker_two,
        ) = await create_sticker_helper(
            test_get_session, johnson_superadmin.id, jayson_user.id
        )
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/stickers?sent=true&received=true",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        print("data['data']: ", data["data"])
        assert (
            data["data"] == "can not have sent=true and received=true at the same time."
        )

    @pytest.mark.asyncio
    async def test_fetch_all_available_stickers(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful all stickers retrieval.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        (
            new_sticker_one,
            new_sticker_two,
            exchanged_sticker_one,
            exchanged_sticker_two,
        ) = await create_sticker_helper(
            test_get_session, johnson_superadmin.id, jayson_user.id
        )
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/stickers",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "All Available Stickers retrieved successfully."
        assert data["data"][0]["id"] == new_sticker_one.id
        assert data["data"][0]["name"] == new_sticker_one.name
        assert data["data"][0]["price"] == new_sticker_one.price
        assert data["data"][0]["url"] == new_sticker_one.url

        assert data["data"][1]["id"] == new_sticker_two.id
        assert data["data"][1]["name"] == new_sticker_two.name
        assert data["data"][1]["price"] == new_sticker_two.price
        assert data["data"][1]["url"] == new_sticker_two.url
