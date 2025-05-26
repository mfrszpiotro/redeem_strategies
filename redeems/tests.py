import random
import string
from decimal import Decimal
from unittest import TestCase, mock
import unittest

from .redeems import AccountNo, PaymentGateway, RedemptionService, User, logger


class UserFactory:
    @staticmethod
    def create() -> User:
        user_id = "".join(random.choices((string.ascii_letters + string.digits), k=5))
        account_no = "".join(random.choices(string.digits, k=20))
        return User(id=user_id, account_no=AccountNo(account_no))


class TestRedemptionService(TestCase):
    def setUp(self) -> None:
        self.payment_gateway = mock.create_autospec(PaymentGateway)
        self.redemption_service = RedemptionService(
            payment_gateway=self.payment_gateway,
        )
        self.exemplary_user = UserFactory.create()
        self.exemplary_sufficient_points = Decimal(1000)
        self.exemplary_insufficient_points = self.exemplary_sufficient_points - 1

    def test_logs_user_redemption(self) -> None:
        with self.assertLogs(logger=logger) as log:
            self.redemption_service.redeem(
                self.exemplary_user, self.exemplary_sufficient_points
            )
        self.assertIn(
            f"Redeemed {self.exemplary_sufficient_points}, for a {self.exemplary_user}",
            log.output[0],
        )
        # todo: self.assertIn inssuficient amount of points case

    def test_uses_payment_gateway_to_transfer_money_to_user(self) -> None:
        user = UserFactory.create()
        amount = Decimal(100)
        self.redemption_service.redeem(user, amount)
        self.payment_gateway.assert_called_once_with(user.account_no, amount)

    @unittest.skip("Not implemented yet")
    def test_strategy_bank_transfer_using_payment_gateway(self) -> None:
        user = UserFactory.create()  # country that uses bank transfer
        sufficient_amount = self.exemplary_sufficient_points
        self.redemption_service.redeem(user, sufficient_amount)
        self.payment_gateway.transfer.assert_called_once_with(
            user.account_no, sufficient_amount
        )

    @unittest.skip("Not implemented yet")
    def test_strategy_gift_card_not_using_payment_gateway(self) -> None:
        user = UserFactory.create()  # country that uses gift card
        sufficient_amount = self.exemplary_insufficient_points
        self.redemption_service.redeem(user, sufficient_amount)
        self.payment_gateway.transfer.assert_not_called()


class TestPaymentGateway(TestCase):
    def test_has_transfer_method(self) -> None:
        account_no = UserFactory.create().account_no
        with self.assertLogs(logger) as log:
            PaymentGateway().transfer(account_no, Decimal(100))
        self.assertIn(
            f"Successfully transferred 100 to {account_no}",
            log.output[0],
        )
