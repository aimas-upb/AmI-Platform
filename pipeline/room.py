from core import PDU

class Room(PDU):
    QUEUE = 'room'

    def process_message(self, message):
        pass

if __name__ == "__main__":
    module = Room()
    module.run()