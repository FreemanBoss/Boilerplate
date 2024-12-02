import pytest

from api.v1.subscriptions.service import subscription_service, subscription_plan_service
from api.v1.user.service import user_service


class TestSubscriptionPlanService:
    """
    Tests class for subscription_plan service.
    """

    @pytest.mark.asyncio
    async def test_create_subscription_plan(
        self,
        mock_johnson_user_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating subscription plan by admin.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        subscription_plan_one = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )

        assert johson_user.email == mock_johnson_user_dict["email"]
        assert (
            mock_subcsription_plan_dict["creator_id"]
            == subscription_plan_one.creator_id
        )
        assert mock_subcsription_plan_dict["duration"] == "weekly"

    @pytest.mark.asyncio
    async def test_fetch_subscription_plan(
        self,
        mock_johnson_user_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for fetching subscription plan by admin.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        _ = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )

        fetched_sub_plan = await subscription_plan_service.fetch(
            {"creator_id": johson_user.id, "duration": "weekly"}, test_get_session
        )

        assert fetched_sub_plan.creator_id == johson_user.id
        assert fetched_sub_plan.duration == "weekly"

    @pytest.mark.asyncio
    async def test_fetch_all_subscription_plan(
        self,
        mock_johnson_user_dict,
        mock_subcsription_plan_dict,
        mock_subcsription_plan_dict_two,
        test_get_session,
        test_setup,
    ):
        """
        Tests for fetching all subscription plan by admin.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        mock_subcsription_plan_dict["creator_id"] = johson_user.id
        mock_subcsription_plan_dict_two["creator_id"] = johson_user.id

        _ = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )
        _ = await subscription_plan_service.create(
            mock_subcsription_plan_dict_two, test_get_session
        )

        fetched_sub_plans = await subscription_plan_service.fetch_all(
            where={
                "creator_id": johson_user.id,
            },
            session=test_get_session,
            filterer={},
        )
        assert fetched_sub_plans[1].duration == "monthly"
        assert fetched_sub_plans[0].duration == "weekly"

    @pytest.mark.asyncio
    async def test_update_subscription_plan(
        self,
        mock_johnson_user_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for updating subscription plan by admin.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        new_sub_plan = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )

        assert new_sub_plan.creator_id == johson_user.id

        _ = await subscription_plan_service.update(
            [
                {"creator_id": johson_user.id, "duration": "weekly"},
                {"duration": "yearly"},
            ],
            test_get_session,
        )
        fetched_sub_plan = await subscription_plan_service.fetch(
            {
                "creator_id": johson_user.id,
            },
            test_get_session,
        )

        assert fetched_sub_plan.creator_id == johson_user.id
        assert fetched_sub_plan.duration == "yearly"

    @pytest.mark.asyncio
    async def test_deleting_subscription_plan(
        self,
        mock_johnson_user_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for deleting subscription plan by admin.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        new_sub_plan = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )

        assert new_sub_plan.creator_id == johson_user.id

        _ = await subscription_plan_service.delete(
            {"creator_id": johson_user.id, "duration": "weekly"}, test_get_session
        )
        fetched_sub_plan = await subscription_plan_service.fetch(
            {
                "creator_id": johson_user.id,
            },
            test_get_session,
        )

        assert fetched_sub_plan == None

    @pytest.mark.asyncio
    async def test_delete_all_subscription_plan(
        self,
        mock_johnson_user_dict,
        mock_subcsription_plan_dict,
        mock_subcsription_plan_dict_two,
        test_get_session,
        test_setup,
    ):
        """
        Tests for deleteing all subscription plan by admin.
        """
        mock_johnson_user_dict.pop("confirm_password")

        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )

        mock_subcsription_plan_dict["creator_id"] = johson_user.id
        mock_subcsription_plan_dict_two["creator_id"] = johson_user.id

        _ = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )
        _ = await subscription_plan_service.create(
            mock_subcsription_plan_dict_two, test_get_session
        )

        fetched_sub_plans = await subscription_plan_service.fetch_all(
            where={
                "creator_id": johson_user.id,
            },
            session=test_get_session,
            filterer={},
        )
        assert fetched_sub_plans[1].duration == "monthly"
        assert fetched_sub_plans[0].duration == "weekly"

        _ = await subscription_plan_service.delete_all(
            where={
                "creator_id": johson_user.id,
            },
            session=test_get_session,
        )

        fetched_sub_plans = await subscription_plan_service.fetch_all(
            where={
                "creator_id": johson_user.id,
            },
            session=test_get_session,
            filterer={},
        )

        assert len(fetched_sub_plans) == 0


class TestSubscriptionService:
    """
    Tests class for subscription service.
    """

    @pytest.mark.asyncio
    async def test_create_subscription(
        self,
        mock_johnson_user_dict,
        mock_jayson_user_dict,
        mock_subcsription_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for creating subscription.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")
        # johnson admin user
        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        # jayson regular user
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_subcsription_dict["subscriber_id"] = jayson_user.id
        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        # create subscription plan by johnson admin
        subscription_plan_one = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )
        mock_subcsription_dict["subscription_plan_id"] = subscription_plan_one.id

        assert johson_user.email == mock_johnson_user_dict["email"]
        assert (
            mock_subcsription_plan_dict["creator_id"]
            == subscription_plan_one.creator_id
        )
        assert mock_subcsription_plan_dict["duration"] == "weekly"

        # jayson subscribe to plan
        jayson_subscription = await subscription_service.create(
            mock_subcsription_dict, test_get_session
        )

        assert jayson_subscription.subscription_plan_id == subscription_plan_one.id
        assert jayson_subscription.status == "active"

    @pytest.mark.asyncio
    async def test_fetch_subscription(
        self,
        mock_johnson_user_dict,
        mock_jayson_user_dict,
        mock_subcsription_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for fetch subscription.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")
        # johnson admin user
        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        # jayson regular user
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_subcsription_dict["subscriber_id"] = jayson_user.id
        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        # create subscription plan by johnson admin
        subscription_plan_one = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )
        mock_subcsription_dict["subscription_plan_id"] = subscription_plan_one.id

        assert johson_user.email == mock_johnson_user_dict["email"]
        assert (
            mock_subcsription_plan_dict["creator_id"]
            == subscription_plan_one.creator_id
        )
        assert mock_subcsription_plan_dict["duration"] == "weekly"

        # jayson subscribe to plan
        jayson_subscription = await subscription_service.create(
            mock_subcsription_dict, test_get_session
        )

        assert jayson_subscription.subscription_plan_id == subscription_plan_one.id
        assert jayson_subscription.status == "active"

        fetched_jayson_subscription = await subscription_service.fetch(
            mock_subcsription_dict, test_get_session
        )

        assert (
            fetched_jayson_subscription.subscription_plan_id == subscription_plan_one.id
        )
        assert fetched_jayson_subscription.status == "active"

    @pytest.mark.asyncio
    async def test_update_subscription(
        self,
        mock_johnson_user_dict,
        mock_jayson_user_dict,
        mock_subcsription_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for update subscription.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")
        # johnson admin user
        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        # jayson regular user
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_subcsription_dict["subscriber_id"] = jayson_user.id
        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        # create subscription plan by johnson admin
        subscription_plan_one = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )
        mock_subcsription_dict["subscription_plan_id"] = subscription_plan_one.id

        assert johson_user.email == mock_johnson_user_dict["email"]
        assert (
            mock_subcsription_plan_dict["creator_id"]
            == subscription_plan_one.creator_id
        )
        assert mock_subcsription_plan_dict["duration"] == "weekly"

        # jayson subscribe to plan
        jayson_subscription = await subscription_service.create(
            mock_subcsription_dict, test_get_session
        )

        assert jayson_subscription.subscription_plan_id == subscription_plan_one.id
        assert jayson_subscription.status == "active"

        # update jayson plan
        _ = await subscription_service.update(
            [mock_subcsription_dict, {"status": "expired"}], test_get_session
        )

        fetched_jayson_subscription = await subscription_service.fetch(
            {"subscriber_id": jayson_user.id}, test_get_session
        )

        assert (
            fetched_jayson_subscription.subscription_plan_id == subscription_plan_one.id
        )
        assert fetched_jayson_subscription.status == "expired"

    @pytest.mark.asyncio
    async def test_delete_subscription_plan_sideeffect(
        self,
        mock_johnson_user_dict,
        mock_jayson_user_dict,
        mock_subcsription_dict,
        mock_subcsription_plan_dict,
        test_get_session,
        test_setup,
    ):
        """
        Tests for that delete subscription plan does not delete users subscriptions.
        """
        mock_johnson_user_dict.pop("confirm_password")
        mock_jayson_user_dict.pop("confirm_password")
        # johnson admin user
        johson_user = await user_service.create(
            mock_johnson_user_dict, test_get_session
        )
        # jayson regular user
        jayson_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_subcsription_dict["subscriber_id"] = jayson_user.id
        mock_subcsription_plan_dict["creator_id"] = johson_user.id

        # create subscription plan by johnson admin
        subscription_plan_one = await subscription_plan_service.create(
            mock_subcsription_plan_dict, test_get_session
        )
        mock_subcsription_dict["subscription_plan_id"] = subscription_plan_one.id

        assert johson_user.email == mock_johnson_user_dict["email"]
        assert (
            mock_subcsription_plan_dict["creator_id"]
            == subscription_plan_one.creator_id
        )
        assert mock_subcsription_plan_dict["duration"] == "weekly"

        # jayson subscribe to plan
        _ = await subscription_service.create(mock_subcsription_dict, test_get_session)
        # delete the subscription plan
        _ = await subscription_plan_service.delete(
            mock_subcsription_plan_dict, test_get_session
        )
        # fetch user subscription.
        fetched_jayson_subscription = await subscription_service.fetch(
            mock_subcsription_dict, test_get_session
        )
        # assert subscription still exists.
        assert (
            fetched_jayson_subscription.subscription_plan_id == subscription_plan_one.id
        )
        assert fetched_jayson_subscription.status == "active"
