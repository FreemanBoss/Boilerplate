import pytest

from api.v1.auth.dependencies import generate_email_verification_token


class TestVerifyEmailRoute:
    """
    Tests class for verifying emails.
    """

    @pytest.mark.asyncio
    async def test_register_verification_success(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for successful verification for user
        """
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "User Registered Successfully"

        user_email_token = await generate_email_verification_token(
            data["data"]["user"]["email"]
        )

        # verify email route

        response = client.get(
            url=f"/api/v1/auth/verify-email?token={user_email_token}",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Account successfully verified."

    @pytest.mark.asyncio
    async def test_verify_user_fake_token(
        self, client, mock_johnson_user_dict, test_setup
    ):
        """
        Test for unsuccessful verification for user
        """
        mock_johnson_user_dict.pop("idempotency_key")
        mock_johnson_user_dict.pop("is_deleted")
        mock_johnson_user_dict.pop("is_suspended")

        response = client.post(url="/api/v1/auth/register", json=mock_johnson_user_dict)

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "User Registered Successfully"

        user_email_token = await generate_email_verification_token(
            "notuseremail@email.com"
        )

        # verify email route

        response = client.get(
            url=f"/api/v1/auth/verify-email?token={user_email_token}",
        )

        assert response.status_code == 400

        data = response.json()

        assert data["message"] == "User not found"
