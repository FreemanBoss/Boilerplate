import pytest

from api.v1.verification_request.service import verification_request_service
from api.v1.user.service import user_service


class TestVerificationRequestService:
    """
    Tests class for verification_request service.
    """

    @pytest.mark.asyncio
    async def test_create_verification_request(
        self, mock_jayson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for creating verification_request.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        jayson_request = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "pending",
                "verified_by_bot": False,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        assert jayson_request.user_to_verify_id == jayson_user.id

    @pytest.mark.asyncio
    async def test_fetch_verification_request(
        self, mock_jayson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for fetch verification_request.
        """
        mock_jayson_user_dict.pop("confirm_password")

        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        _ = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "pending",
                "verified_by_bot": False,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        fetched_jayson_request = await verification_request_service.fetch(
            {
                "user_to_verify_id": jayson_user.id,
            },
            test_get_session,
        )

        assert fetched_jayson_request.user_to_verify_id == jayson_user.id

    @pytest.mark.asyncio
    async def test_update_verification_request(
        self,
        mock_johnson_user_dict,
        mock_jayson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for update verification_request.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")

        # admin johnson
        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        _ = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "pending",
                "verified_by_bot": False,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        updated_jayson_request = await verification_request_service.update(
            [
                {"user_to_verify_id": jayson_user.id},
                {"verifier_id": johson_user.id, "status": "approved"},
            ],
            test_get_session,
        )

        assert updated_jayson_request.status == "approved"
        assert updated_jayson_request.verifier_id == johson_user.id

    @pytest.mark.asyncio
    async def test_delete_verifier_sideeffect(
        self,
        mock_johnson_user_dict,
        mock_jayson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for when an admin is deleted by a superadmin, the verification
        status is not affected.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")

        # admin johnson
        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        _ = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "pending",
                "verified_by_bot": False,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        _ = await verification_request_service.update(
            [
                {"user_to_verify_id": jayson_user.id},
                {"verifier_id": johson_user.id, "status": "approved"},
            ],
            test_get_session,
        )

        # delete admin johnson
        _ = await user_service.delete({"id": johson_user.id}, test_get_session)

        # confirm admin deletion
        deleted_admin_johnson = await user_service.fetch(
            {"id": johson_user.id}, test_get_session
        )

        assert deleted_admin_johnson is None

        # fetch the verification again

        fetched_jayson_request = await verification_request_service.fetch(
            {"user_to_verify_id": jayson_user.id}, test_get_session
        )
        # verification should should exist regardless
        assert fetched_jayson_request.status == "approved"
        assert fetched_jayson_request.verifier_id is not None
