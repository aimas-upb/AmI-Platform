from pdu import PDU

class EchoPDU(PDU):

    def __init__(self, **kwargs):
        self.QUEUE = kwargs.pop('input_queue', 'echo')
        self.OUTPUT_QUEUE = kwargs.pop('output_queue', 'echo_outputs')
        super(EchoPDU, self).__init__(**kwargs)

    def process_message(self, message):
        self.log("Echo-ing message %r" % message)
        self.send_to(self.OUTPUT_QUEUE, message)