import time

from core import PDU
from lib.log import setup_logging

class Room(PDU):
    QUEUE = 'room'

    # 15 mins before 2 consecutive actions for the same person
    SAME_PERSON_THRESHOLD = 15 * 60

    def __init__(self, **kwargs):
        super(Room, self).__init__(**kwargs)
        self.last_person_name = None
        self.last_person_action_took_at = int(time.time())

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

    def should_take_action_for_person_appeared(self, person_name):
        """ Return True iff we should take action for a person having appeared
            in the scenery.

            We take action if:
            - this person is different from the last person
            - this person is the same as the last person, but the last action
              taken for the last person was at least 15 minutes ago.

        """
        if person_name != self.last_person_name:
            self.logger.info("Appeared person has changed from %s to %s" %\
                             (person_name, self.last_person_name))
            return True

        if int(time.time() - self.last_person_action_took_at) >= \
            self.SAME_PERSON_THRESHOLD:
            self.logger.info("Taking action for person %s, even if it's "
                             "the same person, because enough time has ellapsed"
                             % person_name)
            return True
        else:
            self.logger.info("Not taking action for person %s, because it's "
                             "the same person and too little time has ellapsed"
                             % person_name)
            return False


    def process_message(self, message):
        """ Room module receives incoming events from the different pipelines
            like "person X has appeared in front of kinect Y and reacts to
            that kind of events. """

        print message
        event_type = message.get('event_type', '')
        if event_type == 'person_appeared':
            person_name = message['person_name']
            if self.should_take_action_for_person_appeared(person_name):
                self.handle_person_appeared_event(message)

    def handle_person_appeared_event(self, message):
        """ Handle the person appeared event. """

        person_name = message['person_name']

        self.last_person_action_took_at = int(time.time())
        self.last_person_name = person_name

        if person_name == 'andrei@amilab.ro':
            self.play_message("Hello, Andrei. Let me switch on the air "
                              "conditioning for you.")
            self.switch_on_air_conditioning()
        elif person_name == 'diana@amilab.ro':
            self.play_message("Hello, Diana. I know you like it quiet so "
                              "I won't bother you with air conditioning.")
            self.switch_off_air_conditioning()

    def play_message(self, message):
        """ Plays a text message using our text-to-speech system. """
        self.send_to('text-to-speech', {'text': message})

    def switch_on_air_conditioning(self):
        """ Switch on the air conditioning. """
        params = {
            'cmd': 'on',
            'ip': '172.16.4.99',
            'output': '1',
        }
        self.send_to('ip-power', params)

    def switch_off_air_conditioning(self):
        """ Switch on the air conditioning. """
        params = {
            'cmd': 'off',
            'ip': '172.16.4.99',
            'output': '1',
        }
        self.send_to('ip-power', params)

if __name__ == "__main__":
    setup_logging()
    module = Room()
    module.run()
