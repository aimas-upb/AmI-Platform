from core import PDU
from lib.log import setup_logging

class Posture_classifier(PDU):
    QUEUE = 'posture_classifier'

    def process_message(self, message):
        pass

if __name__ == "__main__":
    setup_logging()
    module = Posture_classifier()
    module.run()