from tests.conftest_helper import create_login_payload
import io
import pytest


class TestProfilePhotoReplaceRoute:
    """
    Test class for profile photo replacement route.
    """

    @pytest.mark.asyncio
    async def test_successful_photo_replacement(
        self, client, test_get_session, test_setup, mock_creation
    ):
        """
        Test for successful photo replacement
        """
        johnson_superadmin, jayson_user, lagos, abuja, free_tier, weekly = mock_creation

        login_response = client.post(
            url="/api/v1/auth/login",
            json=create_login_payload("jayson@gmail.com", "Jayson1234@"),
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
        data = response.json()

        assert response.json()["status_code"] == 201
        assert data["message"] == "Profile photos saved successfully."
        photo_id = data["data"][0]["id"]

        file_content = b"Test file content"
        file = io.BytesIO(file_content)
        file.name = "test_file.png"

        response = client.put(
            url=f"/api/v1/profiles/pictures/{photo_id}",
            files={"photo": (file.name, file, "image/png")},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["message"] == "photo replaced successfully"
        assert data["data"]["id"] == photo_id

    @pytest.mark.asyncio
    async def test_unauthorized_user_access(
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

        response = client.put(
            url=f"/api/v1/profiles/pictures/555",
            files={"photo": (file.name, file, "image/png")},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 401
