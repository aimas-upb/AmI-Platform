from core import PDU

class Router(PDU):
    """ PDU that routes incoming measurements from sensors to the
        actual processing pipelines """

    QUEUE = 'measurements'

    def process_message(self, message):
        # Route messages towards mongo-writer
        self.send_to('mongo-writer', message)
        self.send_to('head-crop', message)
        self.send_to('experiments', message)

if __name__ == "__main__":
    module = Router()
    module.run()
