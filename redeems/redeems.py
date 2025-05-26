from dataclasses import dataclass
from decimal import Decimal
import logging
from typing import NewType


logger = logging.getLogger(__name__)


AccountNo = NewType("AccountNo", str)


@dataclass
class User:
    id: str
    account_no: AccountNo


class PaymentGateway:
    def transfer(self, account_no: AccountNo, amount: Decimal) -> None:
        logger.info(f"Successfully transferred {amount} to {account_no}")


class RedemptionService:
    def __init__(self, payment_gateway) -> None:
        self._payment_gateway = payment_gateway

    def redeem(self, user: User, amount: Decimal) -> None:
        # Assumption: user will redeem `amount` of money.
        # We're not supporting other types of awards.
        self._payment_gateway(user.account_no, amount)
        logger.info(f"Redeemed {amount}, for a {user}")
