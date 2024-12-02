from api.v1.sticker.service import sticker_service, exchanged_sticker_service


async def create_sticker_helper(
    test_get_session, johnson_superadmin_id, jayson_user_id
):

    new_sticker_one = await sticker_service.create(
        {
            "name": "oxygen",
            "price": 20.3,
            "url": "someurl",
            "creator_id": johnson_superadmin_id,
            "currency": "USD",
        },
        test_get_session,
    )

    new_sticker_two = await sticker_service.create(
        {
            "name": "rose",
            "price": 20.3,
            "url": "someurl",
            "creator_id": johnson_superadmin_id,
            "currency": "USD",
        },
        test_get_session,
    )

    exchanged_sticker_one = await exchanged_sticker_service.create(
        {
            "sender_id": johnson_superadmin_id,
            "receiver_id": jayson_user_id,
            "sticker_id": new_sticker_one.id,
            "quantity": 23,
        },
        test_get_session,
    )
    exchanged_sticker_two = await exchanged_sticker_service.create(
        {
            "sender_id": jayson_user_id,
            "receiver_id": johnson_superadmin_id,
            "sticker_id": new_sticker_two.id,
            "quantity": 12,
        },
        test_get_session,
    )
    return (
        new_sticker_one,
        new_sticker_two,
        exchanged_sticker_one,
        exchanged_sticker_two,
    )
