import pytest

from api.v1.user.service import user_service

from api.v1.reel.service import reel_service
from api.v1.photo.service import photo_service
from api.v1.product.service import product_service
from api.v1.comment.service import (
    photo_comment_service,
    product_comment_service,
    reel_comment_service,
)
from api.v1.role_and_permission.service import role_service
from api.v1.role_and_permission.model import user_roles


class TestCommentService:
    """
    Tests class for comment service.
    """

    @pytest.mark.asyncio
    async def test_create_photo_comment(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for create photo comment.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        new_photo = await photo_service.create(
            {
                "user_id": johnson_user.id,
                "linked_to": "profile",
                "url": "some url",
                "is_profile_picture": True,
            },
            test_get_session,
        )

        assert new_photo is not None

        photo_comment = await photo_comment_service.create(
            {
                "commenter_id": johnson_user.id,
                "photo_id": new_photo.id,
                "comment_text": "nice photo.",
            },
            test_get_session,
        )

        assert photo_comment is not None

    @pytest.mark.asyncio
    async def test_create_a_product_comment(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for create product comment.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        new_product = await product_service.create(
            {
                "creator_id": johnson_user.id,
            },
            test_get_session,
        )

        assert new_product is not None

        product_comment = await product_comment_service.create(
            {
                "commenter_id": johnson_user.id,
                "product_id": new_product.id,
                "comment_text": "nice!",
            },
            test_get_session,
        )

        assert product_comment is not None

    @pytest.mark.asyncio
    async def test_create_reel_comment(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating reels comment.
        """
        async with test_get_session.begin().session as session:
            mock_jayson_user_dict.pop("confirm_password")
            # regular user jayson

            mock_johnson_user_dict.pop("confirm_password")
            # admin user johnson
            johnson_user = await user_service.create(mock_johnson_user_dict, session)
            role = await role_service.fetch({"name": "admin"}, session)

            stmt = user_roles.insert().values(
                **{"user_id": johnson_user.id, "role_id": role.id}
            )
            await session.execute(stmt)
            await session.commit()

            johnson_reel = None
            await session.refresh(johnson_user)

            if any(role.name == "admin" for role in johnson_user.roles):

                johnson_reel = await reel_service.create(
                    {
                        "creator_id": johnson_user.id,
                        "url": "fakeurl",
                    },
                    session,
                )
            assert johnson_reel is not None

            reel_comment = await reel_comment_service.create(
                {
                    "commenter_id": johnson_user.id,
                    "reel_id": johnson_reel.id,
                    "comment_text": "still nice.",
                },
                session,
            )

            assert reel_comment is not None
