from tests.conftest_helper import create_login_payload
import io
import pytest

from api.v1.user.service import user_service
from api.v1.profile.service import profile_service
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles
from api.v1.verification_request.service import verification_request_service


class TestVerificationRequetRoute:
    """
    Test class for verification route.
    """

    @pytest.mark.asyncio
    async def test_retrieve_verifications_success(
        self, test_get_session, client, test_setup, mock_creation
    ):
        """
        Test for successful retrieval of verifications by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        verification_request = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "pending",
                "verification_count": 0,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        assert verification_request is not None
        assert verification_request.status == "pending"

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.get(
            url="/api/v1/verifications",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 200

        data = reg_response.json()

        assert data["message"] == "Verifications Retrieved Successfully."
        assert data["data"][0]["id"] == verification_request.id
        assert data["limit"] == 10
        assert data["page"] == 1
        assert data["total_pages"] == 1
        assert data["total_items"] == 1

    @pytest.mark.asyncio
    async def test_update_verifications_success(
        self,
        client,
        test_get_session,
        test_setup,
        mock_creation,
    ):
        """
        Test for successful update of verifications by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        verification_request = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "pending",
                "verification_count": 0,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        assert verification_request is not None
        assert verification_request.status == "pending"

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.put(
            url=f"/api/v1/verifications/{verification_request.id}",
            json={"status": "approved"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 201

        data = reg_response.json()

        assert data["message"] == "Verification Updated Successfully."
        assert data["data"]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_update_verifications_failure(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for unsuccessful update of verifications by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        verification_request = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "pending",
                "verification_count": 0,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        assert verification_request is not None
        assert verification_request.status == "pending"

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.put(
            url=f"/api/v1/verifications/{verification_request.id}",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 422

        data = reg_response.json()

        assert data["message"] == "Validation Error."
        assert (
            data["data"]["msg"]
            == "Value error, accepted must be either approved, rejected, or pending."
        )

    @pytest.mark.asyncio
    async def test_update_already_approved_verifications(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful update of already approved verifications by superadmin
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation
        verification_request = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "approved",
                "verification_count": 0,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        assert verification_request is not None
        assert verification_request.status == "approved"

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        reg_response = client.put(
            url=f"/api/v1/verifications/{verification_request.id}",
            json={"status": "approved"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert reg_response.status_code == 201

        data = reg_response.json()

        assert data["message"] == "Verification Already Approved"
        assert data["data"]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_successful_verifications_request(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful creation of verifications by user.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        file_content = b"Test file content"
        file = io.BytesIO(file_content)
        file.name = "test_file.png"

        response = client.post(
            url="/api/v1/verifications/request",
            files={"photo": (file.name, file, "image/png")},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "Verification request created successfully."

    @pytest.mark.asyncio
    async def test_unauthorized_user_verifications_request(
        self,
        client,
    ):
        """
        Test for unauthorized access to route.
        """
        access_token = "fake token"

        file_content = b"Test file content"
        file = io.BytesIO(file_content)
        file.name = "test_file.png"

        response = client.post(
            url="/api/v1/verifications/request",
            files={"photo": (file.name, file, "image/png")},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_successful_already_verified_request(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful for already verified user request.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        verification_request = await verification_request_service.create(
            {
                "user_to_verify_id": jayson_user.id,
                "status": "approved",
                "verification_count": 0,
                "photo_url": "https://fake.com",
            },
            test_get_session,
        )

        assert verification_request is not None
        assert verification_request.status == "approved"

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        file_content = b"Test file content"
        file = io.BytesIO(file_content)
        file.name = "test_file.png"

        response = client.post(
            url="/api/v1/verifications/request",
            files={"photo": (file.name, file, "image/png")},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 409

        data = response.json()

        assert data["message"] == "Verification request already approved."

    @pytest.mark.asyncio
    async def test_successful_validation_of_file_size(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful validation of file size more than 2MB.
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        file_content = b"Test file content" * (2 * 1024 * 1024 + 2)
        file = io.BytesIO(file_content)
        file.name = "test_file.png"

        response = client.post(
            url="/api/v1/verifications/request",
            files={"photo": (file.name, file, "image/png")},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 400

        data = response.json()

        assert data["message"] == "File size exceeds the limit"

    @pytest.mark.asyncio
    async def test_get_successful_verifications_request(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful retrieval of verifications by user.
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
        )

        assert login_response.status_code == 200

        data = login_response.json()

        access_token = data["data"]["access_token"]

        file_content = b"Test file content"
        file = io.BytesIO(file_content)
        file.name = "test_file.png"

        response = client.post(
            url="/api/v1/verifications/request",
            files={"photo": (file.name, file, "image/png")},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "Verification request created successfully."

        response = client.get(
            url="/api/v1/verifications/request",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Verification Retrieved successfully."
        assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_unauthorized_user_verifications_request(
        self,
        client,
    ):
        """
        Test for unauthorized access to GET route.
        """
        access_token = "fake token"

        response = client.get(
            url="/api/v1/verifications/request",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 401
