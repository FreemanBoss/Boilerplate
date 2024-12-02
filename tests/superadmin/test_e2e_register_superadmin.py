import pytest

from api.utils.settings import Config


class TestRegisterSuperadminROute:
    """
    Tests class for registering a superadmin.
    """

    @pytest.mark.asyncio
    async def test_register_superadmin_no_secret(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, no secret_token
        """

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "Johnson1234@",
                "confirm_password": "Johnson1234@",
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, secret_token cannot be empty.",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_wrong_secret(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, wrong secret_token
        """
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 400

        data = response.json()

        assert data["message"] == "Invalid secret."

    @pytest.mark.asyncio
    async def test_register_superadmin_no_email(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, no email
        """
        mock_johnson_user_dict.pop("email")
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "first_name": "johnson",
                "last_name": "oragui",
                "password": "Johnson1234@",
                "confirm_password": "Johnson1234@",
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, email must be provided",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_fake_email_domain(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, fake email domain
        """
        mock_johnson_user_dict["email"] = "johnson@example.com"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@example.com",
                "first_name": "Johnson",
                "last_name": "Oragui",
                "password": "Johnson1234@",
                "confirm_password": "Johnson1234@",
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, example.com is not allowed for registration",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_no_firstname(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, no firstname
        """
        mock_johnson_user_dict.pop("first_name")
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": "",
            "ctx": {"min_length": 3},
            "loc": ["body", "first_name"],
            "msg": "String should have at least 3 characters",
            "type": "string_too_short",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_no_lastname(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, no lastname
        """
        mock_johnson_user_dict.pop("last_name")
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": "",
            "ctx": {"min_length": 3},
            "loc": ["body", "last_name"],
            "msg": "String should have at least 3 characters",
            "type": "string_too_short",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_invalid_char_firstname(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, invalid_char firstname
        """
        mock_johnson_user_dict["first_name"] = "Dennid#"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "Dennid#",
                "last_name": "oragui",
                "password": "Johnson1234@",
                "confirm_password": "Johnson1234@",
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, # is not allowed in first_name",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_invalid_char_lastname(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, invalid_char lastname
        """
        mock_johnson_user_dict["last_name"] = "Johnson@"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": {
                "email": "johnson@gmail.com",
                "first_name": "johnson",
                "last_name": "Johnson@",
                "password": "Johnson1234@",
                "confirm_password": "Johnson1234@",
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, @ is not allowed in last_name",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_invalid_password_length(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, password length
        """
        mock_johnson_user_dict["password"] = "Jo1234#"
        mock_johnson_user_dict["confirm_password"] = "Jo1234#"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            "input": "Jo1234#",
            "ctx": {"min_length": 12},
            "loc": ["body", "password"],
            "msg": "String should have at least 12 characters",
            "type": "string_too_short",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_password_digit(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, password digit
        """
        mock_johnson_user_dict["password"] = "Johnsonjohnson@"
        mock_johnson_user_dict["confirm_password"] = "Johnsonjohnson@"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

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
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, Johnsonjohnson@ must contain at least one digit character",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_password_lowercase_letter(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, password lowercase_letter
        """
        mock_johnson_user_dict["password"] = "JOHNSON1234534343@"
        mock_johnson_user_dict["confirm_password"] = "JOHNSON1234534343@"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

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
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, JOHNSON1234534343@ must contain at least one lowercase letter",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_password_luppercase_letter(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, password luppercase_letter
        """
        mock_johnson_user_dict["password"] = "johnson1234534343@"
        mock_johnson_user_dict["confirm_password"] = "johnson1234534343@"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

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
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, johnson1234534343@ must contain at least one uppercase letter",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_password_not_allowed_char(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, password not allowed char
        """
        mock_johnson_user_dict["password"] = "Johnson1234====@"
        mock_johnson_user_dict["confirm_password"] = "Johnson1234====@"
        mock_johnson_user_dict["secret_token"] = Config.TEST_SUPERADMIN_SECRET

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

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
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": Config.TEST_SUPERADMIN_SECRET,
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, contains invalid characters. Allowed special characters: !@#&-_,.",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_invalid_password_different_from_confirm_password(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin, password different from confirm_password
        """
        mock_johnson_user_dict["password"] = "Johnsonjohnson1@"
        mock_johnson_user_dict["confirm_password"] = "Johnson"
        mock_johnson_user_dict["secret_token"] = (
            "wrongsecretwrongsecretwrongsecretwrongsecret"
        )

        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

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
                "idempotency_key": "johnson_idempotency-key",
                "is_deleted": False,
                "is_suspended": False,
                "secret_token": "wrongsecretwrongsecretwrongsecretwrongsecret",
            },
            "ctx": {"error": {}},
            "loc": ["body"],
            "msg": "Value error, Passwords must match",
            "type": "value_error",
        }

    @pytest.mark.asyncio
    async def test_register_superadmin_success(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful registration for superadmin
        """
        mock_johnson_user_dict["secret_token"] = Config.TEST_SUPERADMIN_SECRET
        response = client.post(
            url="/api/v1/superadmin/register", json=mock_johnson_user_dict
        )

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "User Registered Successfully"
