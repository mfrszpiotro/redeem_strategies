import random
import string
from decimal import Decimal
from unittest import TestCase, mock

from .redeems import (
    AccountNo,
    Points,
    PaymentGateway,
    RedemptionService,
    User,
    UserId,
    logger,
    CountryCode,
    BankTransfer,
)


class UserFactory:
    @staticmethod
    def create(country_code: CountryCode) -> User:
        user_id = UserId(
            "".join(random.choices((string.ascii_letters + string.digits), k=5))
        )
        account_no = AccountNo("".join(random.choices(string.digits, k=20)))
        return User(user_id, Points(Decimal(0)), account_no, country_code)


class TestRedemptionService(TestCase):
    def setUp(self) -> None:
        self.payment_gateway = mock.Mock(spec=["transfer"])
        self.redemption_service = RedemptionService(
            payment_gateway=self.payment_gateway,
        )
        self.exemplary_country_code = CountryCode.DE
        self.exemplary_user = UserFactory.create(self.exemplary_country_code)
        self.exemplary_sufficient_points = (
            self.exemplary_user.redemption_strategy.required_points
        )
        self.exemplary_insufficient_points = Points(
            self.exemplary_sufficient_points - 1
        )

    def test_logs_user_redemption(self) -> None:
        with self.assertLogs(logger=logger) as log:
            self.exemplary_user.points = self.exemplary_sufficient_points
            self.redemption_service.redeem(self.exemplary_user)
            self.exemplary_user.points = self.exemplary_insufficient_points
            self.redemption_service.redeem(self.exemplary_user)
        self.assertIn(
            f"Redeemed {self.exemplary_sufficient_points} points, "
            f"for user {self.exemplary_user.id}",
            log.output[0],
        )
        self.assertIn(
            f"Not enough points, got {self.exemplary_user.points} "
            f"out of {self.exemplary_sufficient_points}",
            log.output[1],
        )

    def test_strategy_bank_transfer_using_payment_gateway(self) -> None:
        user = UserFactory.create(CountryCode.DE)  # country that uses bank transfer
        user.points = user.redemption_strategy.required_points
        self.redemption_service.redeem(user)
        assert isinstance(user.redemption_strategy, BankTransfer)
        self.payment_gateway.transfer.assert_called_once_with(
            user.account_no, user.redemption_strategy.award_amount
        )

    def test_strategy_gift_card_not_using_payment_gateway(self) -> None:
        user = UserFactory.create(CountryCode.FR)  # country that uses gift card
        user.points = user.redemption_strategy.required_points
        self.redemption_service.redeem(user)
        self.payment_gateway.transfer.assert_not_called()


class TestPaymentGateway(TestCase):
    def test_has_transfer_method(self) -> None:
        account_no = UserFactory.create(CountryCode.DE).account_no
        with self.assertLogs(logger=logger) as log:
            PaymentGateway().transfer(account_no, Points(Decimal(100)))
        self.assertIn(
            f"Successfully transferred 100 to {account_no}",
            log.output[0],
        )
