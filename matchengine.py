import os
import sys
from queue import Queue
from threading import Thread
from orderbook import OrderBook
from orderevent import *
from marketdepth import *
from limitorder import Side
import logging
import argparse


logger = logging.getLogger('OrderBook')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(filename=r'data\ouput.log', mode='w')
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)
logger.addHandler(file_handler)



class MatchEngine(Thread):
    """
    matching engine implemented as thread
    it manages incoming order requests from queue
    it will also monitor stats of requests and make descision to scale up
    TODO: hybrid approach for high liquidity price range use FixedArray method and the rest Heap
    """
    def __init__(self, q, method='heap', price_range=None):
        Thread.__init__(self)
        if method == 'heap':
            self.obook = OrderBook('jump', HeapMarketDepth(), HeapMarketDepth())
        else:
            self.obook = OrderBook('jump', FixedArrayMarketDepth(Side.Buy, price_range),
                                   FixedArrayMarketDepth(Side.Sell, price_range))

        self.router = self.obook.router
        self.oqueue = q

    def run(self):
        logger.info('Matching Engine Started')
        while True:
            msg = self.oqueue.get()
            if msg == 'q':
                break
            evt = OrderEventFactory.produce(msg)
            self.router.event_handler(evt)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='matching engine')
    parser.add_argument('--testfile', type=str, nargs='?', help='path to test csv')
    parser.add_argument('--method', type=str, nargs='?', default='heap', help='path to test csv')
    parser.add_argument('--range', type=str, nargs='?', default='', help='required if fixedarray method used')

    args = parser.parse_args()

    order_queue = Queue()
    if args.method == 'heap':
        engine = MatchEngine(order_queue, method=args.method)
    else:
        engine = MatchEngine(order_queue, method=args.method, price_range=list(map(int, args.range.split(','))))
    engine.start()

    if args.testfile:
        another_file_handler = logging.FileHandler(filename=r'data\ouput_{}.log'.format(args.method), mode='w')
        logger.addHandler(another_file_handler)

        if os.path.exists(args.testfile):
            for t in open(args.testfile).readlines():
                order_queue.put(t.strip())

        order_queue.put('q')
        engine.join()
    else:
        value = ''
        while not value == 'q':
            value = input()
            order_queue.put(value)