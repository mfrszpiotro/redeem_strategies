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
    France = "FR"
    Germany = "DE"
    India = "IN"


class PaymentGateway:
    def transfer(self, account_no: AccountNo, money_amount: Decimal) -> None:
        logger.info(f"Successfully transferred {money_amount} to {account_no}")


class RedemptionStrategy(ABC):
    required_points: Points
    award_amount: Decimal

    def __init__(self, required_points: Points, award_amount: Decimal):
        self.required_points = required_points
        self.award_amount = award_amount

    def redeem_points(
        self,
        points: Points,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ) -> bool:
        if self._check_sufficient_points(points):
            self._process_points(payment_gateway, account_no)
            return True
        return False

    def _check_sufficient_points(self, points: Points) -> bool:
        if not points >= self.required_points:
            logger.info(
                f"Not enough points, got {points} out of {self.required_points}"
            )
            return False
        return True

    @abstractmethod
    def _process_points(
        self,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ): ...


class BankTransfer(RedemptionStrategy):
    class MissingPaymentDetailsException(Exception):
        pass

    def _process_points(
        self,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ):
        if payment_gateway and account_no:
            payment_gateway.transfer(account_no, self.award_amount)
            print(
                f"We've sent a transfer to your account {self.award_amount}$ "
                f"for {self.required_points} points. Don't spend it all at once!"
            )
        else:
            raise self.MissingPaymentDetailsException()


class GiftCard(RedemptionStrategy):
    def _process_points(
        self,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ):
        print(
            f"Here is your gift card (amount: {self.award_amount}$) "
            f"for {self.required_points} points. Use it wisely!"
        )


class CinemaTickets(RedemptionStrategy):
    def _process_points(
        self,
        payment_gateway: Optional[PaymentGateway],
        account_no: Optional[AccountNo],
    ):
        print(
            f"Here are your cinema tickets (quantity: {self.award_amount}) "
            f"for {self.required_points} points. Enjoy the silver screen experience!"
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
        if user.redemption_strategy.redeem_points(
            user.points, self._payment_gateway, user.account_no
        ):
            price = user.redemption_strategy.required_points
            user.points = Points(user.points - price)
            print(f"Your point account balance after this redemption: {user.points}")
            logger.info(f"Redeemed {price} points, for user {user.id}")


COUNTRY_STRATEGY_CONFIG: Dict[CountryCode, RedemptionStrategy] = {
    CountryCode.Germany: BankTransfer(Points(Decimal(1000)), Decimal(50)),
    CountryCode.France: GiftCard(Points(Decimal(2000)), Decimal(100)),
    CountryCode.India: CinemaTickets(Points(Decimal(500)), Decimal(2)),
}
