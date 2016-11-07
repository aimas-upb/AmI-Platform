import copy
import json
import logging
import time
import threading
import traceback

import pymongo

from utils import json_dumps
from kestrel_connection import KestrelConnection
import settings


class PDU(object):
    """ Processing Data Unit for our AmI lab pipelines. """

    # Print flow stats every X seconds
    PRINT_STATS_INTERVAL = 30
    MESSAGE_SAMPLING_RATIO = 10

    TIME_TO_SLEEP_ON_BUSY = 0.05
    MAX_BUSY_SLEEPS = 10
    JSON_DUMPS_STRING_LIMIT = 1000

    def __init__(self, **kwargs):
        """ Set-up connections to Mongo and Kestrel by default on each PDU. """
        self.queue_system = kwargs.get('queue_system', None) or KestrelConnection()
        self._mongo_connection = pymongo.Connection(settings.MONGO_SERVER)
        self._last_stats = time.time()
        self._processed_messages = 0
        self._running = False
        self._cancelled = False
        self._cancelled_lock = threading.Lock()
        self.debug_mode = kwargs.get('debug', False)
        self.logger = logging.getLogger(self.__module__)

    def log(self, message, level=logging.INFO):
        """ Log a message to stdout. Includes class name & current time. """
        self.logger.log(level, message)

    @property
    def mongo_connection(self):
        return self._mongo_connection

    def validate_message(self, message):
        return True

    def process_message(self, message):
        raise NotImplemented("Please implement this in your sub-class!")

    def send_to(self, queue, message):
        """ Send a message to another queue. """
        self.log("Enqueueing message to %s" % queue, level=logging.INFO)
        self.queue_system.add(queue, json.dumps(message))

    def _start_running(self):
        """ Mark the current PDU as running. """
        self._running = True

    def _stop_running(self):
        """ Mark the current PDU as NOT running. """
        self._running = False

    def _is_running(self):
        """ Query whether the current PDU is running or not. """
        result = self._running
        return result

    def stop(self):
        self._cancelled_lock.acquire()
        self._cancelled = True
        self._cancelled_lock.release()

    def _is_cancelled(self):
        self._cancelled_lock.acquire()
        _is_cancelled = self._cancelled
        self._cancelled_lock.release()
        return  _is_cancelled

    def busy(self):
        """ Make this return True and fetching of messages from the queue
        system will stall in order to avoid overflows. """
        return False

    def run(self):
        """ Main loop of the PDU.

        It's basically an an infinite loop that tries to read messages
        from the message queue, decode them and them process them with the specific
        function.

        """
        self._start_running()
        self.log("PDU %s is alive!" % self.__class__.__name__)

        while not self._is_cancelled():
            try:
                # While module reports that it's busy, stop feeding
                # messages to it - especially useful for cases where
                # a part of message processing is asynchronous w.r.t.
                # to message fetching. In that case, messages can accumulate
                # in the memory of the PDU, leading to a huge mem usage.
                busy_sleeps = 0
                while self.busy() and busy_sleeps < self.MAX_BUSY_SLEEPS:
                    time.sleep(self.TIME_TO_SLEEP_ON_BUSY)
                if busy_sleeps == self.MAX_BUSY_SLEEPS:
                    continue

                # Step 1 - get message from message queue
                message = self.queue_system.get(self.QUEUE, timeout = 1)
                if not message:
                    """self.log("Could not get message from queue %s Retrying ..."
                             % self.QUEUE)"""
                    continue

                # Step 2 - try to decode it assuming it's in correct
                # JSON format
                try:
                    doc = json.loads(message)
                except:
                    self.log("Did not get valid JSON from queue %s" % self.QUEUE)
                    self.log("Invalid message: %s" % json_dumps(message))
                    continue

                # Step 3 - validate message
                try:
                    copy_of_doc = copy.deepcopy(doc)
                    is_valid = self.validate_message(copy_of_doc)
                    if not is_valid:
                        self.log("Invalid message from queue %s" % self.QUEUE)
                        self.log("Message: %s" % json_dumps(copy_of_doc))
                        continue
                except:
                    self.log("Error while validating message %s from queue %s" %
                             json_dumps(doc), self.QUEUE)
                    traceback.print_exc()
                    continue

                # Step 4 - actually process the message. Usually, this means
                # that a PDU enqueues it further down the pipeline to other
                # modules.
                try:
                    copy_of_doc = copy.deepcopy(doc)
                    self.process_message(copy_of_doc)
                except:
                    self.log("Error while processing message %s from queue %s" %
                             (json_dumps(doc), self.QUEUE))
                    traceback.print_exc()
                    continue

                ratio = self.MESSAGE_SAMPLING_RATIO
                if self.debug_mode and self._processed_messages % ratio == 0:
                    self.log("Sampled message: %s" % json_dumps(doc))

                # Only increment # of processed messages if there was an actual
                # processing. If we do this in the "finally" block, it will
                # also get executed after "continue" statements as well.
                self._processed_messages = self._processed_messages + 1
            except:
                self.log("Error while getting message from queue %s" % self.QUEUE)
                traceback.print_exc()
            finally:
                # Count # of processed messages in each time interval
                # and display them to the log.

                time_since_last_stats = time.time() - self._last_stats
                if time_since_last_stats >= self.PRINT_STATS_INTERVAL:
                    if self._processed_messages > 0:
                        flow = self._processed_messages / time_since_last_stats
                        self.log("%.2f messages/s in last %.2f seconds" % \
                                 (flow, time_since_last_stats))
                    self._processed_messages = 0
                    self._last_stats = time.time()
        self._stop_running()