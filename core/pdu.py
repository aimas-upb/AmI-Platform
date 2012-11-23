import copy
import json
import kestrel
import pymongo

import settings

"""
    Processing Data Unit for our AmI lab pipelines.
"""
class PDU(object):

    def __init__(self):
        """ Set-up connections to Mongo and Kestrel by default on each PDU. """
        self._kestrel_connection = kestrel.Client(settings.KESTREL_SERVERS)
        self._mongo_connection = pymongo.Connection(settings.MONGO_SERVER)

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
                    print "Did not get valid JSON from queue %s" % self.QUEUE
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
