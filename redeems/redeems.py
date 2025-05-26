from decimal import Decimal
import logging
from typing import NewType, Dict, Optional
from abc import abstractmethod, ABC
from enum import Enum


logger = logging.getLogger(__name__)


UserId = NewType("UserId", str)
AccountNo = NewType("AccountNo", str)
Points = NewType("Points", Decimal)


class CountryCode(str, Enum):
    FR = "FR"
    DE = "DE"


class PaymentGateway:
    def transfer(self, account_no: AccountNo, money_amount: Decimal) -> None:
        logger.info(f"Successfully transferred {money_amount} to {account_no}")


class RedemptionStrategy(ABC):
    required_points: Points

    def redeem_points(
        self,
        points: Points,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ):
        if self._check_sufficient_points(points):
            self._process_points(points, payment_gateway, account_no)

    def _check_sufficient_points(self, points: Points) -> bool:
        predicate = points >= self.required_points
        if not predicate:
            logger.info(
                f"Not enough points, got {points} out of {self.required_points}"
            )
        return predicate

    @abstractmethod
    def _process_points(
        self,
        points: Points,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ): ...


class BankTransfer(RedemptionStrategy):
    class MissingPaymentDetailsException(Exception):
        pass

    def __init__(self, required_points: Points, award_amount: Decimal):
        self.required_points = required_points
        self.award_amount = award_amount

    def _process_points(
        self,
        points: Points,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ):
        if payment_gateway and account_no:
            payment_gateway.transfer(account_no, self.award_amount)
            print(
                f"We've sent a transfer to your account "
                f"for {self.award_amount}. Don't spend it all at once!"
            )
        else:
            raise self.MissingPaymentDetailsException()


class GiftCard(RedemptionStrategy):
    def __init__(self, required_points: Points):
        self.required_points = required_points

    def _process_points(
        self,
        points: Points,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ):
        print(
            f"Here is your gift card for redeeming your {points} points. Use it wisely!"
        )


class User:
    def __init__(
        self,
        id: UserId,
        points: Points,
        account_no: AccountNo,
        country_code: CountryCode,
    ) -> None:
        self.id = id
        self.points = points
        self.account_no = account_no
        self.country_code = country_code
        self.redemption_strategy = COUNTRY_STRATEGY_CONFIG[country_code]
        pass


class RedemptionService:
    def __init__(self, payment_gateway: PaymentGateway) -> None:
        self._payment_gateway = payment_gateway

    def redeem(self, user: User) -> None:
        user.redemption_strategy.redeem_points(
            user.points, self._payment_gateway, user.account_no
        )
        logger.info(f"Redeemed {user.points} points, for user {user.id}")


COUNTRY_STRATEGY_CONFIG: Dict[CountryCode, RedemptionStrategy] = {
    CountryCode.DE: BankTransfer(Points(Decimal(1000)), Decimal(50)),
    CountryCode.FR: GiftCard(Points(Decimal(2000))),
}
