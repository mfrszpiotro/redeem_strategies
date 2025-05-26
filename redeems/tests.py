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

    def test_logs_user_redemption(self) -> None:
        parameterized = [
            (
                None,
                f"Not enough points, got {0} "
                f"out of {self.exemplary_user.redemption_strategy.required_points}",
            ),
            (
                self.exemplary_user.redemption_strategy.required_points + 10,
                f"Redeemed {self.exemplary_user.redemption_strategy.required_points} "
                f"points, for user {self.exemplary_user.id}",
            ),
            (
                None,
                f"Not enough points, got {10} "
                f"out of {self.exemplary_user.redemption_strategy.required_points}",
            ),
            (
                self.exemplary_user.redemption_strategy.required_points - 1,
                f"Not enough points, got "
                f"{self.exemplary_user.redemption_strategy.required_points - 1} "
                f"out of {self.exemplary_user.redemption_strategy.required_points}",
            ),
        ]
        with self.assertLogs(logger=logger) as log:
            for points, expected_result in parameterized:
                print(points, self.exemplary_user.points)
                self.exemplary_user.points = Points(
                    points if points is not None else self.exemplary_user.points
                )
                with self.subTest(expected_result):
                    self.redemption_service.redeem(self.exemplary_user)
                    self.assertIn(
                        expected_result,
                        log.output[-1],
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
