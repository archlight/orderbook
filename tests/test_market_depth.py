from unittest import TestCase
from marketdepth import *
from limitorder import *


class TestHeapMarketDepth(TestCase):
    def setUp(self):
        self.marketdepth = HeapMarketDepth()

    def test_sell_heap(self):
        for i, price in enumerate([80, 90, 75, 100, 95, 75]):
            self.marketdepth.push(LimitOrder(i, Side.Sell, 100, price))
        order = self.marketdepth.head()
        self.assertEqual(2, order.orderid)
        self.marketdepth.pop()
        order = self.marketdepth.head()
        self.assertEqual(5, order.orderid)

    def test_buy_heap(self):
        for i, price in enumerate([80, 90, 75, 100, 95, 100]):
            self.marketdepth.push(LimitOrder(i, Side.Buy, 100, price))
        order = self.marketdepth.head()
        self.assertEqual(3, order.orderid)
        self.marketdepth.pop()
        order = self.marketdepth.head()
        self.assertEqual(5, order.orderid)

    def test_sell_array_stepping_price(self):
        self.marketdepth = HeapMarketDepth()
        self.marketdepth.push(LimitOrder(100001, Side.Sell, 120, 106))
        self.marketdepth.push(LimitOrder(100003, Side.Sell, 80, 105))
        self.assertEqual(100003, self.marketdepth.head().orderid)


class TestFixedArrayMarketDepth(TestCase):

    def test_sell_array(self):
        self.marketdepth = FixedArrayMarketDepth(Side.Sell, (6000, 12000))

        for i, price in enumerate([80, 90, 75, 100, 95, 75]):
            self.marketdepth.push(LimitOrder(i, Side.Sell, 100, price))
        order = self.marketdepth.head()
        self.assertEqual(2, order.orderid)
        self.marketdepth.pop()
        order = self.marketdepth.head()
        self.assertEqual(5, order.orderid)

    def test_buy_array(self):
        self.marketdepth = FixedArrayMarketDepth(Side.Buy, (6000, 12000))

        for i, price in enumerate([80, 90, 75, 100, 95, 100]):
            self.marketdepth.push(LimitOrder(i, Side.Buy, 100, price))
        order = self.marketdepth.head()
        self.assertEqual(3, order.orderid)
        self.marketdepth.pop()
        order = self.marketdepth.head()
        self.assertEqual(5, order.orderid)

    def test_buy_array_cancel(self):
        self.marketdepth = FixedArrayMarketDepth(Side.Buy, (6000, 12000))
        order = LimitOrder(51, Side.Buy, 55, 105)
        self.marketdepth.push(order)
        order.status = Status.CANCELLED
        self.marketdepth.remove(order)
        self.marketdepth.push(LimitOrder(52, Side.Buy, 55, 105))
        order = self.marketdepth.head()
        self.assertEqual(52, order.orderid)

    def test_sell_array_same_price(self):
        self.marketdepth = FixedArrayMarketDepth(Side.Sell, (8000, 12000))
        self.marketdepth.push(LimitOrder(100001, Side.Sell, 120, 90))
        self.marketdepth.push(LimitOrder(100002, Side.Sell, 80, 95))
        self.assertEqual(9000, self.marketdepth.head_price_level)

    def test_sell_array_stepping_price(self):
        self.marketdepth = FixedArrayMarketDepth(Side.Sell, (9000, 11000))

        order = LimitOrder(100002, Side.Sell, 100, 92)
        self.marketdepth.push(order)
        order.status = Status.FILLED
        self.marketdepth.remove(order)
        self.assertEqual(0, self.marketdepth.head_price_level)

        self.marketdepth.push(LimitOrder(100001, Side.Sell, 120, 106))

        order = LimitOrder(100002, Side.Sell, 120, 93)
        self.marketdepth.push(order)
        self.assertEqual(9300, self.marketdepth.head_price_level)

        order.status = Status.FILLED
        self.marketdepth.remove(order)
        self.assertEqual(10600, self.marketdepth.head_price_level)

        order = LimitOrder(100003, Side.Sell, 100, 106)
        self.marketdepth.push(order)

        self.marketdepth.push(LimitOrder(100004, Side.Sell, 80, 105))
        self.assertEqual(10500, self.marketdepth.head_price_level)

        self.marketdepth.push(LimitOrder(100005, Side.Sell, 80, 106))
        self.assertEqual(10500, self.marketdepth.head_price_level)

        order.status = Status.CANCELLED
        self.marketdepth.remove(order)

        order = LimitOrder(100002, Side.Sell, 120, 98)
        self.marketdepth.push(order)
        order.status = Status.FILLED
        self.marketdepth.remove(order)
        self.assertEqual(10500, self.marketdepth.head_price_level)

        self.assertEqual(10500, self.marketdepth.head_price_level)



