import pytest

from api.v1.sticker.service import sticker_service, exchanged_sticker_service
from api.v1.user.service import user_service


class TestStickerService:
    """
    Tests class for sticker service.
    """

    @pytest.mark.asyncio
    async def test_create_sticker(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating sticker.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_johnson_user_dict.pop("confirm_password")
        # admin user johnson
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        new_sticker = await sticker_service.create(
            {
                "creator_id": johnson_user.id,
                "name": "new-sticker",
                "price": 5.0,
                "currency": "USD",
                "url": "someurl",
            },
            test_get_session,
        )
        assert new_sticker.creator_id == johnson_user.id
        assert new_sticker.name == "new-sticker"

    @pytest.mark.asyncio
    async def test_update_sticker(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for update sticker.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_johnson_user_dict.pop("confirm_password")
        # admin user johnson
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        new_sticker = await sticker_service.create(
            {
                "creator_id": johnson_user.id,
                "name": "new-sticker",
                "price": 5.0,
                "currency": "USD",
                "url": "someurl",
            },
            test_get_session,
        )

        updated_sticker = await sticker_service.update(
            [{"id": new_sticker.id}, {"price": 10.0}], session=test_get_session
        )
        assert updated_sticker.creator_id == johnson_user.id
        assert updated_sticker.price == 10.0


class TestExchangedStickerService:
    """
    Tests class for exchanged-sticker service.
    """

    @pytest.mark.asyncio
    async def test_create_exchanged_sticker(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating exchangedsticker.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_johnson_user_dict.pop("confirm_password")
        # admin user johnson
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        new_sticker = await sticker_service.create(
            {
                "creator_id": johnson_user.id,
                "name": "new-sticker",
                "price": 5.0,
                "currency": "USD",
                "url": "someurl",
            },
            test_get_session,
        )
        # jayson exchanges sticker by sending to admin
        jayson_send_sticker = await exchanged_sticker_service.create(
            {
                "sender_id": jayson_user.id,
                "receiver_id": johnson_user.id,
                "sticker_id": new_sticker.id,
            },
            test_get_session,
        )

        assert jayson_send_sticker.receiver_id == johnson_user.id
        assert jayson_send_sticker.sticker_id == new_sticker.id
        assert jayson_send_sticker.sender_id == jayson_user.id

    @pytest.mark.asyncio
    async def test_delete_sticker_side_effect(
        self,
        mock_jayson_user_dict,
        mock_johnson_user_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for deleting a sticker creator won't delete users' stickers.
        """
        mock_jayson_user_dict.pop("confirm_password")
        # regular user jayson
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_johnson_user_dict.pop("confirm_password")
        # admin user johnson
        johnson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        new_sticker = await sticker_service.create(
            {
                "creator_id": johnson_user.id,
                "name": "new-sticker",
                "price": 5.0,
                "currency": "USD",
                "url": "someurl",
            },
            test_get_session,
        )
        # jayson exchanges sticker by sending to admin
        _ = await exchanged_sticker_service.create(
            {
                "sender_id": jayson_user.id,
                "receiver_id": johnson_user.id,
                "sticker_id": new_sticker.id,
            },
            test_get_session,
        )

        # delete admin user johnson
        _ = await user_service.delete({"id": johnson_user.id}, test_get_session)
        # confirm delete admin user johnson
        deleted_johnson_user = await user_service.fetch(
            {"id": johnson_user.id}, test_get_session
        )

        assert deleted_johnson_user is None

        # confirm exchanged stickers still exists
        fetched_exchanged_sticker = await exchanged_sticker_service.fetch(
            {
                "sender_id": jayson_user.id,
                "receiver_id": johnson_user.id,
                "sticker_id": new_sticker.id,
            },
            test_get_session,
        )

        assert fetched_exchanged_sticker.receiver_id == johnson_user.id
        assert fetched_exchanged_sticker.sticker_id == new_sticker.id
        assert fetched_exchanged_sticker.sender_id == jayson_user.id
