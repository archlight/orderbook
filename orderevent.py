from limitorder import LimitOrder
from enum import Enum
from decimal import Decimal


class OrderErrorMessage(Enum):
    BadMessageFormat = 101
    UnsupportedMessageType = 102
    DuplicateOrderId = 201
    RejectedByOrderBook = 301


class AddOrderRequest:

    def __init__(self, id: int, orderid: int, side: int, quantity: int, price: Decimal):
        self.id = id
        self.orderid = orderid
        self.side = side
        self.quantity = quantity
        self.price = price

    def toLimitOrder(self):
        return LimitOrder(self.orderid, self.side, self.quantity, self.price)

    def __eq__(self, other):
        return isinstance(other, AddOrderRequest) \
               and (self.id, self.orderid, self.side, self.quantity, self.price) \
               == (other.id, other.orderid, other.side, other.quantity, other.price)

    def __str__(self):
        return ",".join(map(str, [self.id, self.orderid, self.side, self.quantity, self.price]))


class CancelOrderRequest:

    def __init__(self, id: int, orderid: int):
        self.id = id
        self.orderid = orderid

    def __eq__(self, other):
        return isinstance(other, CancelOrderRequest) \
               and (self.id, self.orderid) == (other.id, other.orderid)

    def __str__(self):
        return ",".join(map(str, [self.id, self.orderid]))


class TradeEvent:

    def __init__(self, quantity: int, price: Decimal):
        self.id = 2
        self.quantity = quantity
        self.price = price

    def __eq__(self, other):
        return isinstance(other, TradeEvent) \
               and (self.id, self.quantity, self.price) == (other.id, other.quantity, other.price)

    def __str__(self):
        return ",".join(map(str, [self.id, self.quantity, self.price]))


class OrderFullyFilled:

    def __init__(self, orderid: int):
        self.id = 3
        self.orderid = orderid

    def __eq__(self, other):
        return isinstance(other, OrderFullyFilled) \
               and (self.id, self.orderid) == (other.id, other.orderid)

    def __str__(self):
        return ",".join(map(str, [self.id, self.orderid]))


class OrderPartiallyFilled:

    def __init__(self, orderid: int, quantity: int, aggressive: bool):
        self.id = 4
        self.orderid = orderid
        self.quantity = quantity
        self.aggressive = aggressive

    def __eq__(self, other):
        return isinstance(other, OrderPartiallyFilled) \
               and (self.id, self.orderid, self.quantity, self.aggressive) \
               == (other.id, other.orderid, other.quantity, other.aggressive)

    def __str__(self):
        return ",".join(map(str, [self.id, self.orderid, self.quantity]))


class ErrorEvent:

    def __init__(self, message: OrderErrorMessage):
        self.id = 5
        self.message = message

    def __str__(self):
        return self.message.name


class OrderEventFactory:

    @classmethod
    def produce(cls, msg):
        try:
            tokens = list(map(lambda x: Decimal(x) if '.' in x else int(x), msg.split(',')))
            if tokens[0] == 0:
                return AddOrderRequest(*tokens)
            elif tokens[0] == 1:
                return CancelOrderRequest(*tokens)
            else:
                return ErrorEvent(OrderErrorMessage.UnsupportedMessageType)
        except Exception as _:
            return ErrorEvent(OrderErrorMessage.BadMessageFormat)
