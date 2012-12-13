from core import PDU

class Room(PDU):
    QUEUE = 'room'

    def validate_message(self, message):
        """ All messages towards the room module must have
            an event_type field.

            If event_type == 'person_appeared', then the format of the
            message is:
                {'event_type': 'person_appeared',
                 'person_name': 'obama@ami-lab.ro'}
        """
        if 'event_type' not in message:
            return False

        if 'event_type' == 'person_appeared':
            if 'person_name' not in message:
                return False

        return True

    def process_message(self, message):
        """ Room module receives incoming events from the different pipelines
            like "person X has appeared in front of kinect Y and reacts to
            that kind of events. """

        print message
        event_type = message.get('event_type', '')
        if event_type == 'person_appeared':
            self.handle_person_appeared_event(message)

    def handle_person_appeared_event(self, message):
        """ Handle the person appeared event. """

        person_name = message['person_name']
        if person_name == 'andrei@amilab.ro':
            self.play_message("Hello, Andrei. Let me switch on the air "
                              "conditioning for you.")
            self.switch_on_air_conditioning()
        elif person_name == 'liviu@amilab.ro':
            self.play_message("Hello, Diana. I know you like it quiet so "
                              "I won't bother you with air conditioning.")
            self.switch_off_air_conditioning()

    def play_message(self, message):
        """ Plays a text message using our text-to-speech system. """
        self.send_to('text_to_speech', {'text': message})

    def switch_on_air_conditioning(self):
        """ Switch on the air conditioning. """
        params = {
            'cmd': 'on',
            'ip': '192.168.0.30',
            'output': '1',
        }
        self.send_to('ip_power', params)

    def switch_off_air_conditioning(self):
        """ Switch on the air conditioning. """
        params = {
            'cmd': 'off',
            'ip': '192.168.0.30',
            'output': '1',
        }
        self.send_to('ip_power', params)

if __name__ == "__main__":
    module = Room()
    module.run()