import pymongo

from core import PDU
from core import constants

class Router(PDU):
    """ PDU that routes incoming measurements from sensors to the
        actual processing pipelines """

    QUEUE = 'measurements'

    def process_message(self, message):
        # Route messages towards mongo-writer
        self.send_to('mongo-writer', message)

if __name__ == "__main__":
    module = Router()
    module.run()
