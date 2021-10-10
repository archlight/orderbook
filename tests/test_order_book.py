from unittest import TestCase
from orderbook import OrderBook
from limitorder import LimitOrder, Side, Status
from orderevent import *
from marketdepth import *


class OrderBookTestCase(TestCase):

    def setUp(cls):
        cls.book = None
        cls.router = None

    def _test_orderbook_stats(self):
        self.assertEqual(len(self.book.position), self.book.volume() + self.book.stats.fully_filled + self.book.stats.cancelled)
        self.assertEqual(sum([1 for k, v in self.book.position.items() if v.status == Status.CANCELLED]), self.book.stats.cancelled)
        self.assertEqual(sum([1 for k, v in self.book.position.items() if v.status == Status.FILLED]), self.book.stats.fully_filled)

    def fully_filled_buy_order(self):
        before = len(self.router.event_seq)
        self.book.add(LimitOrder(100000, Side.Sell, 100, 100))
        self.book.add(LimitOrder(100001, Side.Buy, 100, 120))  # aggresive order
        self.assertEqual(before + 3, len(self.router.event_seq))
        self.assertTrue(TradeEvent(100, 100), self.router.event_seq[-3:])
        self.assertIn(OrderFullyFilled(100001), self.router.event_seq[-3:])
        self.assertIn(OrderFullyFilled(100000), self.router.event_seq[-3:])
        self.assertEqual(0, len(self.book.marketdepth[Side.Buy]))
        self.assertEqual(0, len(self.book.marketdepth[Side.Sell]))
        self._test_orderbook_stats()

    def partially_filled_sell_order(self):
        before = len(self.router.event_seq)
        self.book.add(LimitOrder(100002, Side.Buy, 100, 100))
        self.book.add(LimitOrder(100003, Side.Sell, 200, 90))  # aggresive order
        self.assertEqual(len(self.router.event_seq), before + 3)
        self.assertTrue(TradeEvent(100, 100), self.router.event_seq[-3:])
        self.assertIn(OrderPartiallyFilled(100003, 100, True), self.router.event_seq[-3:])
        self.assertIn(OrderFullyFilled(100002), self.router.event_seq[-3:])
        self._test_orderbook_stats()

    def partially_then_fully_filled_buy_order(self):
        self.book.add(LimitOrder(100004, Side.Sell, 120, 90))
        self.book.add(LimitOrder(100005, Side.Sell, 80, 100))
        self.book.add(LimitOrder(100006, Side.Buy, 200, 110))
        self.assertIn(TradeEvent(120, 90), self.router.event_seq)
        self.assertIn(OrderPartiallyFilled(100006, 80, True), self.router.event_seq)
        self.assertIn(OrderFullyFilled(100004), self.router.event_seq)
        self.assertIn(TradeEvent(80, 100), self.router.event_seq)
        self.assertIn(OrderFullyFilled(100006), self.router.event_seq)
        self.assertIn(OrderFullyFilled(100005), self.router.event_seq)
        self._test_orderbook_stats()

    def cancel_then_rest_order(self):
        self.book.add(LimitOrder(100001, Side.Sell, 120, 90))
        self.book.add(LimitOrder(100002, Side.Buy, 80, 80))
        self.book.cancel(100002)
        self.book.add(LimitOrder(100003, Side.Sell, 80, 80))
        self.assertEqual(0, len(self.router.event_seq))
        self._test_orderbook_stats()

    def cancel_then_fill_order(self):
        self.book.add(LimitOrder(100001, Side.Sell, 120, 90))
        self.book.add(LimitOrder(100002, Side.Sell, 80, 95))
        self.book.add(LimitOrder(100003, Side.Buy, 80, 80))
        self.book.cancel(100001)
        self.book.add(LimitOrder(100004, Side.Buy, 80, 95))
        self.assertIn(TradeEvent(80, 95), self.router.event_seq)
        self.assertIn(OrderFullyFilled(100002), self.router.event_seq)
        self.assertIn(OrderFullyFilled(100004), self.router.event_seq)
        self._test_orderbook_stats()

class OrderBookWithHeapTestCase(OrderBookTestCase):


    def setUp(cls):
        cls.book = OrderBook('test-heap', HeapMarketDepth(), HeapMarketDepth())
        cls.router = cls.book.router

    def test_fully_filled_buy_order(self):
        self.fully_filled_buy_order()

    def test_partially_filled_sell_order(self):
        self.partially_filled_sell_order()

    def test_partially_then_fully_filled_buy_order(self):
        self.partially_then_fully_filled_buy_order()

    def test_cancel_then_rest_order(self):
        self.cancel_then_rest_order()

    def test_cancel_then_fill_order(self):
        self.cancel_then_fill_order()


class OrderBookWithFixedArrayTestCase(OrderBookTestCase):

    def setUp(self):
        self.book = OrderBook('test-fixedarray', FixedArrayMarketDepth(Side.Buy, [8000, 12000]),
                              FixedArrayMarketDepth(Side.Sell, [8000, 12000]))
        self.router = self.book.router

    def test_fully_filled_buy_order(self):
        self.fully_filled_buy_order()

    def test_partially_filled_sell_order(self):
        self.partially_filled_sell_order()

    def test_partially_then_fully_filled_buy_order(self):
        self.partially_then_fully_filled_buy_order()

    def test_cancel_then_rest_order(self):
        self.cancel_then_rest_order()

    def test_cancel_then_fill_order(self):
        self.cancel_then_fill_order()
