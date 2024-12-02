from tests.conftest_helper import create_login_payload
import pytest

from api.utils.settings import Config
from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles


class TestLoginRoute:
    """
    Test class for login route.
    """

    @pytest.mark.asyncio
    async def test_login_no_email(self, client, test_setup, mock_creation):
        """
        Test for unsuccessful login for superadmin, no email
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login", json={"email": "", "password": "Johnson1234@"}
        )

        assert login_response.status_code == 422

        data = login_response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {"email": "", "password": "Johnson1234@"},
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, email must be provided.",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_login_superadmin_fake_email_domain(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful login, fake email domain
        """
        mock_johnson_user_dict["secret_token"] = Config.TEST_SUPERADMIN_SECRET
        register_response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert register_response.status_code == 201

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@test.com", "Johnson1234@")
        )

        assert login_response.status_code == 400

        data = login_response.json()

        assert (
            data["message"]
            == "Email domain does not have valid MX records, contact your domain provider."
        )
        assert data["data"] == {}

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_setup, mock_creation):
        """
        Test for successful login
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        assert data["message"] == "Login Successful"
        assert "profile" in data["data"]
        assert "user" in data["data"]
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    @pytest.mark.asyncio
    async def test_login_email_not_verified(
        self, client, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Test for unsuccessful login, email not verified
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_johnson_user_dict["email_verified"] = False
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        _ = await profile_service.create({"user_id": new_user.id}, test_get_session)

        assert new_user is not None

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 401

        data = login_response.json()

        msg = "Email not verified, check your inbox or spam. If link has expired, request for another link with the email used for registration"

        assert data["message"] == msg
        assert "profile" not in data["data"]
        assert "user" not in data["data"]
        assert "access_token" not in data["data"]
        assert "refresh_token" not in data["data"]

    @pytest.mark.asyncio
    async def test_login_unsuccess_not_exist_email(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful login, with non-existing user email, and right password.
        """
        mock_johnson_user_dict["secret_token"] = Config.TEST_SUPERADMIN_SECRET
        register_response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert register_response.status_code == 201

        password = mock_johnson_user_dict["password"]
        email = "jayson@gmail.com"
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload(email, password)
        )

        assert login_response.status_code == 401

        data = login_response.json()

        assert data["message"] == "Invalid email or password"
        assert "profile" not in data["data"]
        assert "user" not in data["data"]
        assert "access_token" not in data["data"]
        assert "refresh_token" not in data["data"]

    @pytest.mark.asyncio
    async def test_login_unsuccess_wrong_password(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful login, with wrong password, and right email.
        """
        mock_johnson_user_dict["secret_token"] = Config.TEST_SUPERADMIN_SECRET
        register_response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert register_response.status_code == 201

        password = "Jayson1234@"
        email = mock_johnson_user_dict["email"]
        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload(email, password)
        )

        assert login_response.status_code == 401

        data = login_response.json()

        assert data["message"] == "Invalid email or password"
        assert "profile" not in data["data"]
        assert "user" not in data["data"]
        assert "access_token" not in data["data"]
        assert "refresh_token" not in data["data"]

    @pytest.mark.asyncio
    async def test_login_user_is_not_active(
        self, client, test_get_session, mock_johnson_user_dict, test_setup
    ):
        """
        Test for login, user not active
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_johnson_user_dict["is_active"] = False
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        _ = await profile_service.create({"user_id": new_user.id}, test_get_session)

        assert new_user is not None

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 403

        data = login_response.json()

        assert data["message"] == "User is inactive"
        assert "profile" not in data["data"]
        assert "user" not in data["data"]
        assert "access_token" not in data["data"]
        assert "refresh_token" not in data["data"]

    @pytest.mark.asyncio
    async def test_login_user_is_suspended(
        self, client, test_get_session, mock_johnson_user_dict, test_setup
    ):
        """
        Test for login, user is suspended
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_johnson_user_dict["is_suspended"] = True
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        _ = await profile_service.create({"user_id": new_user.id}, test_get_session)

        assert new_user is not None

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 403

        data = login_response.json()

        assert data["message"] == "User is still suspended"
        assert "profile" not in data["data"]
        assert "user" not in data["data"]
        assert "access_token" not in data["data"]
        assert "refresh_token" not in data["data"]

    @pytest.mark.asyncio
    async def test_login_user_is_deleted(
        self, client, test_get_session, mock_johnson_user_dict, test_setup
    ):
        """
        Test for login, user deleted
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_johnson_user_dict["is_deleted"] = True
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        _ = await profile_service.create({"user_id": new_user.id}, test_get_session)

        assert new_user is not None

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 403

        data = login_response.json()

        assert data["message"] == "User is no longer a part of the platform."
        assert "profile" not in data["data"]
        assert "user" not in data["data"]
        assert "access_token" not in data["data"]
        assert "refresh_token" not in data["data"]
