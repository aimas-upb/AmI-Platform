import time
from unittest import TestCase

from nose.tools import eq_

from core import ParallelPDU

def heavy_preprocess(message):
    """ Dummy heavy preprocessing function which sleeps for a given amount
        of seconds specified in the message. """
    if 'sleep' in message:
        time.sleep(message['sleep'])

class MyParallelPDU(ParallelPDU):
    """ Dummy implementation of a parallel PDU. It has 2 main functionalities:

        - receive ORDERED_DELIVERY from the kwargs
        - register the order in which light_postprocess processes the messages.
    """
    def __init__(self, **kwargs):
        super(MyParallelPDU, self).__init__(**kwargs)
        if 'ORDERED_DELIVERY' in kwargs:
            self.ORDERED_DELIVERY = kwargs['ORDERED_DELIVERY']
        self.processed = []

    def light_postprocess(self, actual_result, message):
        self.processed.append(message)

class ParallelPDUTest(TestCase):

    def test_pdu_processes_all_messages(self):
        """ Tests that the parallel PDU successfully processes all messages. """

        pdu = MyParallelPDU(heavy_preprocess = heavy_preprocess)
        pdu.process_message({'id': 1})
        pdu.process_message({'id': 2})
        time.sleep(1)
        eq_(len(pdu.processed), 2, "PDU should have processed 2 messages")
        ids = set([x.get('id', None) for x in pdu.processed])
        eq_(ids, set([1, 2]), "PDU processed messages should have correct IDs")

    def test_pdu_processes_heavier_message_last(self):
        """ If processing 2 messages and the 1st one takes longer to process,
            the 2nd one should finish processing first.

            This is because by default, parallel pdu's have ordered delivery
            set to false.
        """

        pdu = MyParallelPDU(heavy_preprocess = heavy_preprocess)
        pdu.process_message({'id': 1, 'sleep': 2})
        pdu.process_message({'id': 2, 'sleep': 1})
        time.sleep(2.5)
        eq_(len(pdu.processed), 2, "PDU should have processed 2 messages")
        ids = [x.get('id', None) for x in pdu.processed]
        eq_(ids, [2, 1], "PDU processed messages should have correct order")

    def test_pdu_ordered_delivery_message_heaviness_doesnt_matter(self):
        """ If processing 2 messages, although the first one takes
            longer to process, it should get processed first because of
            ordered delivery. """

        pdu = MyParallelPDU(heavy_preprocess = heavy_preprocess,
                            ORDERED_DELIVERY = True)
        pdu.process_message({'id': 1, 'sleep': 2})
        pdu.process_message({'id': 2, 'sleep': 1})
        time.sleep(2.5)
        eq_(len(pdu.processed), 2, "PDU should have processed 2 messages")
        ids = [x.get('id', None) for x in pdu.processed]
        eq_(ids, [1, 2], "PDU processed messages should have correct order")