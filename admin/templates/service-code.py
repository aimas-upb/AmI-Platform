from core import PDU

class {{service_class_name}}(PDU):
    QUEUE = '{{service_queue}}'

    def process_message(self, message):
        pass

if __name__ == "__main__":
    module = {{service_class_name}}()
    module.run()
