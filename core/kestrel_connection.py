import logging
import json

import kestrel

import settings

logger = logging.getLogger(__name__)


class KestrelConnection(kestrel.Client):
    """ Wrapper for pykestrel for easier init of connection, sending and
    receiving JSON messages from queues.
    """

    JSON_DUMPS_STRING_LIMIT = 50
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
                        (queue_name, self._json_dumps(raw_message)))
            
        logger.debug("Got message from queue %s: %s" %
                     (queue_name, self._json_dumps(decoded_message)))
        
        return decoded_message
    
    def send_to(self, queue_name, message):
        logger.debug("Sending message to %s: %s" %
                     (queue_name, self._json_dumps(message)))
        
        return self.add(queue_name, json.dumps(message))
    
    def _json_dumps(self, dictionary):
        """ Custom version of json.dumps which truncates long string fields. """
        return json.dumps(self._truncate_strs(dictionary))
    
    def _truncate_strs(self, dictionary):
        """ Given a dictionary, explore it using depth first search (DFS)
        and truncate the values of keys which are "too long".
        
        """
        # Edge case - dictionary is in fact not a dictionary, but a string
        if type(dictionary) != dict:
            result = str(dictionary)
            if len(result) > self.JSON_DUMPS_STRING_LIMIT:
                result = result[0:self.JSON_DUMPS_STRING_LIMIT] + '... (truncated)'
            return result

        result = {}
        for k, v in dictionary.iteritems():
            # If value is a dictionary, recursively truncate big strings
            if type(v) == dict:
                result[k] = self._truncate_strs(v)
            # If it's a large string, truncate it
            elif (type(v) == str or type(v) == unicode) and len(v) > self.JSON_DUMPS_STRING_LIMIT:
                result[k] = v[0:self.JSON_DUMPS_STRING_LIMIT] + '... (truncated)'
            # Otherwise, copy any type of thing
            else:
                result[k] = v
        return result
