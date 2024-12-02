from tests.conftest_helper import create_login_payload
import pytest

from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles


class TestSuperAdminRegisterUserRoute:
    """
    Test class for superadmin register users route.
    """

    @pytest.mark.asyncio
    async def test_register_user_success(self, client, test_setup, mock_creation):
        """
        Test for successful users registration by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.post(
            url="/api/v1/superadmin/users/register",
            json={
                "email": "Jane@gmail.com",
                "password": "Jane1234567@",
                "confirm_password": "Jane1234567@",
                "role": "admin",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 201

        data = reg_response.json()

        assert data["message"] == "User Registered Successfully"

    @pytest.mark.asyncio
    async def test_register_user_idempotency_success(
        self, client, test_setup, mock_creation
    ):
        """
        Test for successful user registration idempotency by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.post(
            url="/api/v1/superadmin/users/register",
            json={
                "email": "Jane@gmail.com",
                "password": "Jane1234567@",
                "confirm_password": "Jane1234567@",
                "role": "admin",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 201

        data = reg_response.json()

        assert data["message"] == "User Registered Successfully"

        reg_response = client.post(
            url="/api/v1/superadmin/users/register",
            json={
                "email": "Jane@gmail.com",
                "password": "Jane1234567@",
                "confirm_password": "Jane1234567@",
                "role": "admin",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 201

        data = reg_response.json()

        assert data["message"] == "User Already Registered."

    @pytest.mark.asyncio
    async def test_register_user_by_non_superuser(
        self, client, test_setup, mock_creation
    ):
        """
        Test for unsuccessful users registration by non superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.post(
            url="/api/v1/superadmin/users/register",
            json={
                "email": "Jane@gmail.com",
                "password": "Jane1234567@",
                "confirm_password": "Jane1234567@",
                "role": "admin",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 401

        data = reg_response.json()

        assert data["message"] == "You have no Authorized access to this resource."

    @pytest.mark.asyncio
    async def test_register_user_unmatched_passwords(
        self, client, test_setup, mock_creation
    ):
        """
        Test for unsuccessful user registration by superadmin: unmatched passwords.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        login_response = client.post(
            url="/api/v1/superadmin/users/register",
            json={
                "email": "Jane@gmail.com",
                "password": "Jane1234567@",
                "confirm_password": "Jane123457@",
                "role": "admin",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert login_response.status_code == 422

        data = login_response.json()

        assert data["message"] == "Validation Error."
        assert data["data"]["msg"] == "Value error, Passwords must match"

    @pytest.mark.asyncio
    async def test_register_user_invalid_role(self, client, test_setup, mock_creation):
        """
        Test for unsuccessful user registration by superadmin: invalid role.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        login_response = client.post(
            url="/api/v1/superadmin/users/register",
            json={
                "email": "Jane@gmail.com",
                "password": "Jane1234567@",
                "confirm_password": "Jane1234567@",
                "role": "fake",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert login_response.status_code == 400

        data = login_response.json()

        assert (
            data["message"] == "Role does not exist, create a new role and try again."
        )
