import logging
import json

import kestrel

import settings
from utils import json_dumps

logger = logging.getLogger(__name__)


class KestrelConnection(kestrel.Client):
    """ Wrapper for pykestrel for easier init of connection, sending and
    receiving JSON messages from queues.
    """


    TIMEOUT = 1

    def __init__(self):
        super(KestrelConnection, self).__init__(settings.KESTREL_SERVERS)

    def fetch_from(self, queue_name):
        # Try to fetch the message & bail out if it fails
        raw_message = self.get(queue_name, timeout=self.TIMEOUT)
        if not raw_message:
            logger.info("Timed out when fetching message from %s" % queue_name)
            return None

        # Try to decode the raw message into JSON
        try:
            decoded_message = json.loads(raw_message)
        except:
            logger.info("Invalid JSON message from %s: %s" %
                        (queue_name, json_dumps(raw_message)))

        logger.debug("Got message from queue %s: %s" %
                     (queue_name, json_dumps(decoded_message)))

        return decoded_message

    def send_to(self, queue_name, message):
        logger.debug("Sending message to %s: %s" %
                     (queue_name, json_dumps(message)))

        return self.add(queue_name, json.dumps(message))


