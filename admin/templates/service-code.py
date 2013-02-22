from core import PDU
from lib.logging import setup_logging

class {{service_class_name}}(PDU):
    QUEUE = '{{service_queue}}'

    def process_message(self, message):
        pass

if __name__ == "__main__":
    setup_logging()
    module = {{service_class_name}}()
    module.run()
