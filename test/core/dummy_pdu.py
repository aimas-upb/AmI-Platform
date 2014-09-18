from core import EchoPDU


class DummyPDU(EchoPDU):
    def __init__(self, **kwargs):
        kwargs['input_queue'] = 'measurements'
        kwargs['output_queue'] = 'dummy'
        super(DummyPDU, self).__init__(**kwargs)
