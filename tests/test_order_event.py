from unittest import TestCase
from orderevent import OrderEventFactory, ErrorEvent, OrderErrorMessage


class TestOrderEventFactory(TestCase):

    def test_bad_message_fromat(self):
        event = OrderEventFactory.produce("1,1000,3,80,100")
        self.assertIsInstance(event, ErrorEvent)
        self.assertEqual(event.message, OrderErrorMessage.BadMessageFormat)

    def test_unsupported_request(self):
        event = OrderEventFactory.produce("3,1000,0,80,100")
        self.assertIsInstance(event, ErrorEvent)
        self.assertEqual(event.message, OrderErrorMessage.UnsupportedMessageType)

