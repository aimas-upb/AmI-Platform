from core import PDU
from lib.log import setup_logging

class SessionProcessor(PDU):
    QUEUE = 'session_processor'

    def process_message(self, message):
        pass

if __name__ == "__main__":
    setup_logging()
    module = SessionProcessor()
    module.run()
