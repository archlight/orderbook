from orderevent import *
import logging

logger = logging.getLogger('OrderBook')


class OrderEventRouter:
    def __init__(self, ob):
        self.obook = ob
        self.router = [
            self.add_event_handler,
            self.cancel_event_handler,
            self.trade_event_handler,
            self.fill_event_handler,
            self.partial_fill_event_handler,
            self.error_event_handler
        ]
        self.event_seq = []

    def event_handler(self, event):
        logger.info(event)
        self.event_seq.append(event)
        self.router[event.id](event)

        # buy, sell = self.obook.marketdepth[Side.Buy].head(), self.obook.marketdepth[Side.Sell].head()
        # logger.info('{}-{} {}'.format(buy.orderid if buy else '', sell.orderid if sell else '', str(event)))

    def add_event_handler(self, event: AddOrderRequest):
        self.obook.add(event.toLimitOrder())

    def cancel_event_handler(self, event: CancelOrderRequest):
        self.obook.cancel(event.orderid)

    def trade_event_handler(self, event: TradeEvent):
        pass

    def fill_event_handler(self, event: OrderFullyFilled):
        self.obook.fill(event.orderid)

    def partial_fill_event_handler(self, event: OrderPartiallyFilled):
        self.obook.partial_fill(event.orderid, event.quantity)
        if event.aggressive:
            self.obook.cross(self.obook.position[event.orderid])

    def error_event_handler(self, event: ErrorEvent):
        pass