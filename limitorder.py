from enum import Enum
from decimal import Decimal

class Side(Enum):
    Buy = 0
    Sell = 1


class Status(Enum):
    LIVE = 0
    PARTIAL_FILLED = 1
    FILLED = 2
    CANCELLED = 3


class WrongSidedOrderException(Exception):
    pass


class LimitOrder:

    """
    limitorder implementation
    price - decimal with two decimal point precision.
    """
    def __init__(self, orderid: int, side: int, quantity: int, price: Decimal):
        self.orderid = orderid
        self.side = Side(side)
        self.quantity = quantity
        self.price = price
        self.status = Status.LIVE

    """x100 to create integer level for fixedarray based orderbook"""
    @property
    def price_level(self):
        return self.price * 100

    """LIVE and PARTIAL_FILLED are executable and stay in orderbook"""
    def executable(self):
        return self.status == Status.LIVE or self.status == Status.PARTIAL_FILLED

    """
    require precision timestamp to differentiate order
    to use heap based order book, order id needs to be ascending order
    status with cancel and filled will return False
    """
    def __lt__(self, other):
        if self.side == other.side:
            if self.price == other.price:
                return self.orderid < other.orderid

            if self.side == Side.Buy:
                return self.price > other.price
            else:
                return self.price < other.price
        raise WrongSidedOrderException()

    def __eq__(self, other):
        return self.orderid == other.orderid
