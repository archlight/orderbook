from ordereventrouter import OrderEventRouter
from orderevent import *
from limitorder import *
from marketdepth import *


class OrderBookStats:
    """
    stats for orderbook
    """
    def __init__(self):
        self.live = 0
        self.cancelled = 0
        self.fully_filled = 0
        self.partial_filled = 0


class OrderBook:
    """
    implementation of limit order OrderBook
    it contains two market depth for buy and sell implemented as heap or fixed array
    name -- name of OrderBook
    buydepth -- market depth of buy orders
    selldepth -- market depth of sell orders
    """
    def __init__(self, name: str, buydepth: MarketDepth, selldepth: MarketDepth):
        self.name = name
        self.marketdepth = {Side.Buy: buydepth, Side.Sell: selldepth}
        self.router = OrderEventRouter(self)
        self.cb = self.router.event_handler
        self.position = dict()
        self.stats = OrderBookStats()

    """
    add order to market depth
    for aggressive order it will execute if it is best price. it will ends up to three scenarios
    """
    def add(self, order: LimitOrder):
        if order.orderid in self.position:
            self.cb(ErrorEvent(OrderErrorMessage.DuplicateOrderId))
        else:
            self.position[order.orderid] = order
            if self.is_immediately_executable(order):
                self.cross(order)

            if order.executable():
                self.marketdepth[order.side].push(order)

    """fully fill an order given orderid"""
    def fill(self, orderid):
        if orderid in self.position:
            self.position[orderid].status = Status.FILLED
            self.stats.fully_filled += 1

            mdepth = self.marketdepth[self.position[orderid].side]
            mdepth.remove(self.position[orderid])

    """cancel an order given orderid"""
    def cancel(self, orderid):
        if orderid in self.position:
            if not self.position[orderid].status == Status.FILLED:
                self.position[orderid].status = Status.CANCELLED
                self.stats.cancelled += 1

            mdepth = self.marketdepth[self.position[orderid].side]
            mdepth.remove(self.position[orderid])

    """partial fill requires only modify quantity in place"""
    def partial_fill(self, orderid, remaining):
        self.position[orderid].quantity = remaining
        self.position[orderid].status = Status.PARTIAL_FILLED

    """get head order given side of marketdepth"""
    def get_head_order_from_side(self, side):
        return self.marketdepth[side].head()

    def is_immediately_executable(self, order):
        if self.marketdepth[order.side].head():
            return order < self.marketdepth[order.side].head()
        else:
            return True

    """
    cross will always initiate from aggressive order
    cross will occurs when resting order price in favor to aggressive side
    buy low and sell high at price indicated by resting order
    each cross will generate three events
    TradeEvent/OrderFullyFilled/OrderPartiallyFilled or TradeEvent/OrderFullyFilled/OrderFullyFilled
    """
    def cross(self, agg_order):
        if agg_order:
            rest_order = self.get_head_order_from_side(Side(not agg_order.side.value))
            if rest_order and rest_order.executable():
                if (agg_order.side == Side.Buy and agg_order.price >= rest_order.price) or \
                        (agg_order.side == Side.Sell and agg_order.price <= rest_order.price):
                    self.cb(TradeEvent(min(agg_order.quantity, rest_order.quantity), rest_order.price))
                    if agg_order.quantity == rest_order.quantity:
                        self.cb(OrderFullyFilled(agg_order.orderid))
                        self.cb(OrderFullyFilled(rest_order.orderid))
                    elif agg_order.quantity > rest_order.quantity:
                        self.cb(OrderFullyFilled(rest_order.orderid))
                        self.cb(OrderPartiallyFilled(agg_order.orderid, agg_order.quantity-rest_order.quantity, True))
                    else:
                        self.cb(OrderFullyFilled(agg_order.orderid))
                        self.cb(OrderPartiallyFilled(rest_order.orderid, rest_order.quantity-agg_order.quantity, False))

    def volume(self):
        return len(self.marketdepth[Side.Buy])+len(self.marketdepth[Side.Sell])

    def market_depth_visual(self):
        pass

    def backup(self):
        pass
