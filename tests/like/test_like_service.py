import pytest

from api.v1.user.service import user_service
from api.v1.like.service import (
    photo_comment_like_service,
    photo_like_service,
    product_comment_like_service,
    product_like_service,
    reel_comment_like_service,
    reel_like_service,
)
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


class TestLikeService:
    """
    Tests class for like service.
    """

    @pytest.mark.asyncio
    async def test_create_photo_like(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for create photo like.
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

        photo_like = await photo_like_service.create(
            {"liker_id": johnson_user.id, "photo_id": new_photo.id}, test_get_session
        )

        assert photo_like is not None

    @pytest.mark.asyncio
    async def test_create_a_product_like(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for create product like.
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

        product_like = await product_like_service.create(
            {"liker_id": johnson_user.id, "product_id": new_product.id},
            test_get_session,
        )

        assert product_like is not None

        product_like = await product_like_service.create(
            {"liker_id": johnson_user.id, "product_id": new_product.id},
            test_get_session,
        )

        assert product_like is not None

    @pytest.mark.asyncio
    async def test_create_reel_like(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating reels like.
        """
        async with test_get_session.begin().session as session:
            mock_jayson_user_dict.pop("confirm_password")
            # regular user jayson
            jayson_user = await user_service.create(mock_jayson_user_dict, session)
            mock_johnson_user_dict.pop("confirm_password")
            # admin user johnson
            johnson_user = await user_service.create(mock_johnson_user_dict, session)
            role = await role_service.fetch({"name": "admin"}, session)

            stmt = user_roles.insert().values(
                **{"user_id": johnson_user.id, "role_id": role.id}
            )
            await session.execute(stmt)
            await session.commit()
            await session.refresh(johnson_user)

            johnson_reel = None

            if johnson_user.roles[0].name == "admin":

                johnson_reel = await reel_service.create(
                    {
                        "creator_id": johnson_user.id,
                        "url": "fakeurl",
                    },
                    session,
                )
            assert johnson_reel is not None

            reel_like = await reel_like_service.create(
                {"liker_id": johnson_user.id, "reel_id": johnson_reel.id}, session
            )

            assert reel_like is not None

    @pytest.mark.asyncio
    async def test_create_photo_comment_like(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for create photo comment like.
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

        photo_comment_like = await photo_comment_like_service.create(
            {
                "liker_id": johnson_user.id,
                "photo_comment_id": photo_comment.id,
            },
            test_get_session,
        )

        assert photo_comment_like is not None

    @pytest.mark.asyncio
    async def test_create_a_product_comment_like(
        self, mock_johnson_user_dict, test_get_session, test_setup
    ):
        """
        Tests for create product comment like.
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

        product_comment_like = await product_comment_like_service.create(
            {
                "liker_id": johnson_user.id,
                "product_comment_id": product_comment.id,
            },
            test_get_session,
        )

        assert product_comment_like is not None

    @pytest.mark.asyncio
    async def test_create_reel_comment_like(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating reels comment like.
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
            await session.refresh(johnson_user)

            johnson_reel = None

            if johnson_user.roles[0].name == "admin":

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

            reel_comment_like = await reel_comment_like_service.create(
                {
                    "liker_id": johnson_user.id,
                    "reel_comment_id": reel_comment.id,
                },
                session,
            )

            assert reel_comment_like is not None
