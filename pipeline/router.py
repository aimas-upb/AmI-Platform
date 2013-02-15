import time
from core import PDU

class Router(PDU):
    """ PDU that routes incoming measurements from sensors to the
        actual processing pipelines """

    QUEUE = 'measurements'

    def process_message(self, message):
        # Route messages towards mongo-writer

        # created_at = time at which message arrived on the router
        message['created_at'] = int(time.time())

        self.send_to('mongo-writer', message)
        self.send_to('head-crop', message)
        self.send_to('experiments', message)
        self.send_to('recorder', message)

if __name__ == "__main__":
    module = Router()
    module.run()
