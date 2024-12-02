import pytest

from api.utils.settings import Config


class TestRegisterRegularUserROute:
    """
    Tests class for registering regular users.
    """

    @pytest.mark.asyncio
    async def test_register_user_no_email(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, no email
        """
        mock_johnson_user_dict.pop("email")
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "Johnson1234@",
                "confirm_password": "Johnson1234@",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, email must be provided",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_user_fake_email_domain(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, fake email domain
        """
        mock_johnson_user_dict["email"] = "johnson@example.com"
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@example.com",
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "Johnson1234@",
                "confirm_password": "Johnson1234@",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, example.com is not allowed for registration",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_user_invalid_password_length(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, password length
        """
        mock_johnson_user_dict["password"] = "Jo1234#"
        mock_johnson_user_dict["confirm_password"] = "Jo1234#"
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": "Jo1234#",
            "ctx": {"min_length": 8},
            "loc": ["body", "password"],
            "msg": "String should have at least 8 characters",
            "type": "string_too_short",
        }

    @pytest.mark.asyncio
    async def test_register_user_password_digit(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, password digit
        """
        mock_johnson_user_dict["password"] = "Johnsonjohnson@"
        mock_johnson_user_dict["confirm_password"] = "Johnsonjohnson@"
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "Johnsonjohnson@",
                "confirm_password": "Johnsonjohnson@",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, Johnsonjohnson@ must contain at least one digit character",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_user_password_lowercase_letter(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, password lowercase_letter
        """
        mock_johnson_user_dict["password"] = "JOHNSON1234534343@"
        mock_johnson_user_dict["confirm_password"] = "JOHNSON1234534343@"
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "JOHNSON1234534343@",
                "confirm_password": "JOHNSON1234534343@",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, JOHNSON1234534343@ must contain at least one lowercase letter",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_user_password_luppercase_letter(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, password luppercase_letter
        """
        mock_johnson_user_dict["password"] = "johnson1234534343@"
        mock_johnson_user_dict["confirm_password"] = "johnson1234534343@"
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "johnson1234534343@",
                "confirm_password": "johnson1234534343@",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, johnson1234534343@ must contain at least one uppercase letter",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_user_password_not_allowed_char(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, password not allowed char
        """
        mock_johnson_user_dict["password"] = "Johnson1234====@"
        mock_johnson_user_dict["confirm_password"] = "Johnson1234====@"
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "Johnson1234====@",
                "confirm_password": "Johnson1234====@",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, contains invalid characters. Allowed special characters: !@#&-_,.",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_user_invalid_password_different_from_confirm_password(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user, password different from confirm_password
        """
        mock_johnson_user_dict["password"] = "Johnsonjohnson1@"
        mock_johnson_user_dict["confirm_password"] = "Johnson"
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "Johnsonjohnson1@",
                "confirm_password": "Johnson",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, Passwords must match",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user
        """
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "User Registered Successfully"
        assert data["data"]["user"]["roles"] == ["user"]

    @pytest.mark.asyncio
    async def test_register_user_success_idempotency(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for user
        """
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "User Registered Successfully"

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "User Already Registered."
        assert data["data"]["user"]["roles"] == ["user"]
