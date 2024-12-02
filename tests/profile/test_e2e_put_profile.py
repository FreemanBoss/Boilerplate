from tests.conftest_helper import create_login_payload
import pytest


class TestProfileUpdateFields:
    """
    Test class for profile update route.
    """

    @pytest.mark.asyncio
    async def test_update_user_profile(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": ["Football", "Writing"],
            "lifestyle_habits": ["yes, i drink", "i smoke sometimes"],
            "family_plans": {"have_kids": "I have Kids"},
            "religion": "Atheist",
            "political_view": "Liberal",
            "bio": "I love reading...",
            "genotype": "AA",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 200

    @pytest.mark.asyncio
    async def test_update_user_profile_hobbies_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update validation
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": "Writing",
            "lifestyle_habits": ["yes, i drink", "i smoke sometimes"],
            "family_plans": {"have_kids": "I have Kids"},
            "religion": "Atheist",
            "political_view": "Liberal",
            "bio": "I love reading...",
            "genotype": "AA",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
        assert response.json()["message"] == "Validation Error."
        assert (
            response.json()["data"]["msg"]
            == "Value error, hobbies must be a list of hobbies"
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_lifestyle_habits_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update validation
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": ["Football", "Writing"],
            "lifestyle_habits": {"sometimes": "sometimes"},
            "family_plans": {"have_kids": "I have Kids"},
            "religion": "Atheist",
            "political_view": "Liberal",
            "bio": "I love reading...",
            "genotype": "AA",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
        assert response.json()["message"] == "Validation Error."
        assert (
            response.json()["data"]["msg"]
            == "Value error, lifestyle_habits must be a list, slice or an array"
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_family_plans_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update validation
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": ["Football", "Writing"],
            "lifestyle_habits": ["yes, i drink", "i smoke sometimes"],
            "family_plans": ["have_kids", "I have Kids"],
            "religion": "Atheist",
            "political_view": "Liberal",
            "bio": "I love reading...",
            "genotype": "AA",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
        assert response.json()["message"] == "Validation Error."
        assert (
            response.json()["data"]["msg"]
            == "Value error, family_plans must be of type json, hashed-map, object, or dictionary"
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_religion_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update validation
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": ["Football", "Writing"],
            "lifestyle_habits": ["yes, i drink", "i smoke sometimes"],
            "family_plans": {"have_kids": "I have Kids"},
            "religion": True,
            "political_view": "Liberal",
            "bio": "I love reading...",
            "genotype": "AA",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
        assert response.json()["message"] == "Validation Error."
        assert (
            response.json()["data"]["msg"]
            == "Value error, religion must be a list of type string"
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_political_view_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update validation
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": ["Football", "Writing"],
            "lifestyle_habits": ["yes, i drink", "i smoke sometimes"],
            "family_plans": {"have_kids": "I have Kids"},
            "religion": "Atheist",
            "political_view": ["Liberal"],
            "bio": "I love reading...",
            "genotype": "AA",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
        assert response.json()["message"] == "Validation Error."
        assert (
            response.json()["data"]["msg"]
            == "Value error, political_view must be  of type string"
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_bio_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update validation
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": ["Football", "Writing"],
            "lifestyle_habits": ["yes, i drink", "i smoke sometimes"],
            "family_plans": {"have_kids": "I have Kids"},
            "religion": "Atheist",
            "political_view": "Liberal",
            "bio": "l",
            "genotype": "AA",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
        assert response.json()["message"] == "Validation Error."
        assert (
            response.json()["data"]["msg"] == "String should have at least 6 characters"
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_genotype_validation(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful user update validation
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]
        profile_id = data["data"]["profile"]["id"]

        profile_data = {
            "hobbies": ["Football", "Writing"],
            "lifestyle_habits": ["yes, i drink", "i smoke sometimes"],
            "family_plans": {"have_kids": "I have Kids"},
            "religion": "Atheist",
            "political_view": "Liberal",
            "bio": "I love reading...",
            "genotype": "A",
        }

        response = client.put(
            url=f"/api/v1/profiles/{profile_id}",
            json=profile_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 422
        assert response.json()["message"] == "Validation Error."
        assert response.json()["data"]["msg"] == "Value error, Invalid genotype"
