import heapq
from collections import deque
from abc import ABC, abstractmethod
from limitorder import LimitOrder


class MarketDepth(ABC):
    def __init__(self):
        self.data = []

    @abstractmethod
    def push(self, item):
        return

    @abstractmethod
    def pop(self):
        return

    @abstractmethod
    def head(self):
        return

    @abstractmethod
    def remove(self, item):
        return

    def __len__(self):
        return len(self.data)


class HeapMarketDepth(MarketDepth):

    def __init__(self):
        super(HeapMarketDepth, self).__init__()

    def push(self, item):
        heapq.heappush(self.data, item)

    """pop ensure the root order is executable"""
    def pop(self):
        heapq.heappop(self.data)
        item = self.head()
        while item and not item.executable():
            try:
                heapq.heappop(self.data)
                item = self.head()
            except IndexError as _:
                break

    def head(self):
        if len(self.data):
            return self.data[0]

    """only head can be removed but if next available still not executable then keep popping"""
    def remove(self, order):
        if self.head() and self.head().orderid == order.orderid:
            self.pop()


class FixedArrayMarketDepth(MarketDepth):

    """
    fixed range of array with deque for each price level
    head_price_level keeps track of best price
    side - Buy/Sell to indicate direction of depth
    price_range - boundary of price array
    """
    def __init__(self, side, price_range=None):
        super(FixedArrayMarketDepth, self).__init__()
        self.price_range = price_range if price_range else [1, 10000]
        self.offset = price_range[0]
        self.data = [deque() for _ in range(price_range[0], price_range[1] + 1)]
        self.head_price_level = 0
        self.count = 0
        self.side = side
        self.multiplier = 1 if side == side.Sell else -1

    """push item for its price level and update head_price_level if item is best executable"""
    def push(self, item: LimitOrder):
        if self.side == item.side and self.price_range[0] <= item.price_level <= self.price_range[1]:
            if not self.head_price_level:
                self.head_price_level = item.price_level
            elif item.price_level * self.multiplier < self.head_price_level * self.multiplier:
                self.head_price_level = item.price_level
            self.data[item.price_level - self.offset].append(item)
            self.count += 1

    """post pop action move to next best deque if current is empty"""
    def pop(self):
        item = self.data[self.head_price_level - self.offset].popleft()
        self.count -= 1

        if not len(self.data[self.head_price_level - self.offset]):
            self.move_to_next()

        return item

    """from current head_price_level search down the array up if Sell or down if Buy"""
    def move_to_next(self):
        i = self.head_price_level + self.multiplier
        while self.price_range[0] <= i <= self.price_range[1]:
            if len(self.data[i - self.offset]):
                self.head_price_level = i
                break
            i += self.multiplier

        if i > self.price_range[1] or i < self.price_range[0]:
            self.head_price_level = 0

    def head(self):
        return self.data[self.head_price_level - self.offset][0] \
            if self.head_price_level and len(self.data[self.head_price_level - self.offset]) else None

    """
    order from OrderFullyFilled if deque empty then skip 
    """
    def remove(self, order: LimitOrder):
        current = self.data[order.price_level - self.offset]
        if len(current):
            try:
                current.remove(order)
                self.count -= 1
                if not len(current) and order.price_level == self.head_price_level:
                    self.move_to_next()
            except ValueError as _:
                pass

    def __len__(self):
        return self.count
