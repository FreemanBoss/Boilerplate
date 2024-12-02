from tests.conftest_helper import create_login_payload
import io
import pytest

from api.v1.setting.service import setting_service


class TestProfileUpdate:
    """
    Test class for profile photo Upload route.
    """

    @pytest.mark.asyncio
    async def test_successful_4_photo_upload(self, client, test_setup, mock_creation):
        """
        Test for successful upload with 4 photos
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "Profile photos saved successfully."
        for photo in response.json()["data"]:
            assert "https://fakePhoto_url.com" == photo["url"]

    @pytest.mark.asyncio
    async def test_successful_5_photo_upload(self, client, test_setup, mock_creation):
        """
        Test for successful upload with 5 photos
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "Profile photos saved successfully."

    @pytest.mark.asyncio
    async def test_successful_6_photo_upload(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful upload with 6 photos
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "Profile photos saved successfully."

    @pytest.mark.asyncio
    async def test_unsuccessful_3_photo_upload(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for unsuccessful upload with 3
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 400
        assert (
            response.json()["message"]
            == "You must provide between 4 and 6 profile photos"
        )

    @pytest.mark.asyncio
    async def test_successful_7_photo_upload(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for unsuccessful upload with 7 photos
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 400
        assert (
            response.json()["message"]
            == "You must provide between 4 and 6 profile photos"
        )

    @pytest.mark.asyncio
    async def test_successful_4_initial_photo_upload_then_2(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for two upload calls within the maximum 6 profile pictures limit
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        # Initial upload of 4 photos
        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "Profile photos saved successfully."
        assert len(response.json()["data"]) == 4
        for photo in response.json()["data"]:
            assert "https://fakePhoto_url.com" == photo["url"]

        # Try to upload 2 more photos
        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "Profile photos saved successfully."
        assert len(response.json()["data"]) == 2
        for photo in response.json()["data"]:
            assert "https://fakePhoto_url.com" == photo["url"]

    @pytest.mark.asyncio
    async def test_unsuccessful_3_photo_upload_after_successful_4(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for two upload calls outside the maximum 6 profile pictures limit
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        # Initial upload of 4 photos
        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 201
        assert response.json()["message"] == "Profile photos saved successfully."
        assert len(response.json()["data"]) == 4
        for photo in response.json()["data"]:
            assert "https://fakePhoto_url.com" == photo["url"]

        # Try to upload 3 more photos
        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 400
        assert (
            response.json()["message"] == "You can only add up to 2 additional photos"
        )

    @pytest.mark.asyncio
    async def test_unsupported_file_type_upload(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for unsuccessful upload with unsupported file type
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.jpg", file, "image/jpeg")),
                ("photos", ("photo2.jpg", file, "image/jpeg")),
                ("photos", ("photo3.jpg", file, "image/jpeg")),
                ("photos", ("photo4.jpg", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 415
        assert response.json()["message"] == "Unsupported file type."

    @pytest.mark.asyncio
    async def test_large_file_upload(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for unsuccessful upload with large file size
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content" * (2 * 1024 * 1024 + 2)
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.json()["status_code"] == 400
        assert response.json()["message"] == "File size exceeds the limit"

    @pytest.mark.asyncio
    async def test_with_unauthenticated_user(
        self, client, test_get_session, test_setup, user
    ):
        """
        Test for unauthenticated user
        """

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("johnson@gmail.com", "Johnson1234@"),
        )
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data["data"]["access_token"]

        # Creating file-like objects
        file_content = b"Test file content"
        file = io.BytesIO(file_content)

        response = client.post(
            url="/api/v1/profiles/pictures",
            files=[
                ("photos", ("photo1.png", file, "image/png")),
                ("photos", ("photo2.png", file, "image/png")),
                ("photos", ("photo3.png", file, "image/png")),
                ("photos", ("photo4.png", file, "image/png")),
            ],
        )

        assert response.json()["status_code"] == 401
        assert response.json()["message"] == "Not authenticated"
