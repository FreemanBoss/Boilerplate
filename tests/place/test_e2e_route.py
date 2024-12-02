from tests.conftest_helper import create_login_payload
import pytest


class TestPlaceRoute:
    """
    Test class for place route.
    """

    @pytest.mark.asyncio
    async def test_search_place_with_free(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for successful place retrieval.
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url=f"/api/v1/places/{res_place_abuja.id}?category=restaurant",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Place retrieved Successfully."

    @pytest.mark.asyncio
    async def test_fetch_a_place_free(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for unsuccessful place retrieval by free_tier user.
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url=f"/api/v1/places/{res_place_abuja.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Place retrieved Successfully."

    @pytest.mark.asyncio
    async def test_fetch_a_place(self, client, test_setup, place_location_subscription):
        """
        Test for successful places retrieval.
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/places?category=restaurant",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Places Retrieved Successfully."
        assert data["data"][0]["id"] == res_place_abuja.id
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_successful_fetch_places_by_search(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for successful places retrieval by search by a free tier with same location
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/places/search?category=restaurant&city=abuja",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Places Retrieved Successfully."
        assert data["data"][0]["id"] == res_place_abuja.id
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_unsuccessful_fetch_places_by_search_diff_location(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for unsuccessful places retrieval by search by a free tier with different location
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/places/search?category=restaurant&place_name=hotel",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 401

        data = response.json()

        assert data["message"] == "User is on a free tier plan."

    @pytest.mark.asyncio
    async def test_fetch_place_category(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for successful retrieveal of place_category
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/places/categories",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Place-Categories Retrieved Successfully."
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_successful_validation_for_category(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for successful category validation in params
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/places",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == "Category is missing in the query parameters."

    @pytest.mark.asyncio
    async def test_successful_validation_for_nonexisting_category(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for successful category validation in params
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/places?category=fake",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        data = response.json()

        assert data["message"] == "Category does not exist."

    @pytest.mark.asyncio
    async def test_unsuccessful_fetch_places_by_search_different_city(
        self, client, test_setup, place_location_subscription
    ):
        """
        Test for unsuccessful places retrieval by search by a free tier with different location
        """
        res_place_abuja, hotel_place_lagos = place_location_subscription

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        response = client.get(
            url="/api/v1/places/search?category=restaurant&city=lagos",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 401

        data = response.json()

        assert data["message"] == "User is on a free tier plan."
