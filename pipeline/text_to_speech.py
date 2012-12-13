from core import PDU

class Text_to_speech(PDU):
    QUEUE = 'text_to_speech'

    def process_message(self, message):
        pass

if __name__ == "__main__":
    module = Text_to_speech()
    module.run()