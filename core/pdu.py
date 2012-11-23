import copy
import json
import kestrel
import pymongo
import time

import settings

"""
    Processing Data Unit for our AmI lab pipelines.
"""
class PDU(object):

    PRINT_STATS_INTERVAL = 30 # Print flow stats every X seconds

    def __init__(self):
        """ Set-up connections to Mongo and Kestrel by default on each PDU. """
        self._kestrel_connection = kestrel.Client(settings.KESTREL_SERVERS)
        self._mongo_connection = pymongo.Connection(settings.MONGO_SERVER)
        self._last_stats = time.time()
        self._processed_messages = 0

    def log(self, message):
        """ Log a message to stdout. Includes class name & current time. """
        msg = '[%s] - %s - %s' % (time.ctime(), self.__class__.__name__,
                                  message)
        print msg

    @property
    def kestrel_connection(self):
        return self._kestrel_connection

    @property
    def mongo_connection(self):
        return self._mongo_connection

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

        while True:
            try:
                # Step 1 - get message from kestrel queue
                message = self.kestrel_connection.get(self.QUEUE, timeout = 1)
                if not message:
                    print "Could not get message from queue %s Retrying ..." % self.QUEUE
                    continue

                # Step 2 - try to decode it assuming it's in correct
                # JSON format
                try:
                    doc = json.loads(message)
                except:
                    print "Did not get valid JSON from queue %s" % QUEUE
                    print "Message = %s" % message
                    import traceback
                    traceback.print_exc()
                    continue

                # Step 3 - actually process the message. Usually, this means
                # that a PDU enqueues it further down the pipeline to other
                # modules.
                copy_of_doc = copy.deepcopy(doc)
                self.process_message(copy_of_doc)

            except:
                print "Error while getting message from queue %s" % self.QUEUE
                import traceback
                traceback.print_exc()
            finally:
                # Count # of processed messages in each time interval
                # and display them to the log.
                self._processed_messages = self._processed_messages + 1
                time_since_last_stats = time.time() - self._last_stats
                if time_since_last_stats >= self.PRINT_STATS_INTERVAL:
                    flow = self._processed_messages / time_since_last_stats
                    self.log("%.2f messages/s in last %.2f seconds" % \
                             (flow, time_since_last_stats))
                    self._processed_messages = 0
                    self._last_stats = time.time()