import copy
import json
import sys
import time
import traceback

import kestrel
import pymongo

import settings

"""
    Processing Data Unit for our AmI lab pipelines.
"""
class PDU(object):

    PRINT_STATS_INTERVAL = 30 # Print flow stats every X seconds
    MESSAGE_SAMPLING_RATIO = 10

    def __init__(self, **kwargs):
        """ Set-up connections to Mongo and Kestrel by default on each PDU. """
        self._kestrel_connection = kestrel.Client(settings.KESTREL_SERVERS)
        self._mongo_connection = pymongo.Connection(settings.MONGO_SERVER)
        self._last_stats = time.time()
        self._processed_messages = 0
        self.debug_mode = kwargs.get('debug', False)

    def log(self, message):
        """ Log a message to stdout. Includes class name & current time. """
        msg = '[%s] - %s - %s' % (time.ctime(), self.__class__.__name__,
                                  message)
        print msg
        sys.stdout.flush()

    @property
    def kestrel_connection(self):
        return self._kestrel_connection

    @property
    def mongo_connection(self):
        return self._mongo_connection

    def validate_message(self, message):
        return True

    def process_message(self, message):
        raise NotImplemented("Please implement this in your sub-class!")

    def send_to(self, queue, message):
        """ Send a message to another queue. """
        self.kestrel_connection.add(queue, json.dumps(message))

    def run(self):
        """ Main loop of the PDU.

        It's basically an an infinite loop that tries to read messages
        from Kestrel, decode them and them process them with the specific
        function.

        """

        self.log("PDU %s is alive!" % self.__class__.__name__)
        while True:
            try:
                # Step 1 - get message from kestrel queue
                message = self.kestrel_connection.get(self.QUEUE, timeout = 1)
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
                    self.log("Message = %s" % message)
                    continue

                # Step 3 - validate message
                try:
                    copy_of_doc = copy.deepcopy(doc)
                    is_valid = self.validate_message(copy_of_doc)
                    if not is_valid:
                        self.log("Invalid message from queue %s" % self.QUEUE)
                        self.log("Message: %s" % json.dumps(copy_of_doc))
                        continue
                except:
                    self.log("Error while validating message %s from queue %s" %
                             json.dumps(doc), self.QUEUE)
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
                             (json.dumps(doc), self.QUEUE))
                    traceback.print_exc()
                    continue
                    
                ratio = self.MESSAGE_SAMPLING_RATIO
                if self.debug_mode and self._processed_messages % ratio == 0:
                    self.log("Sampled message: %s" % json.dumps(doc))
                
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
