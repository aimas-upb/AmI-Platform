import os

from core import PDU
from lib.log import setup_logging

class TextToSpeech(PDU):
    """ Plays back a text message using the espeak text-to-speech system. """

    QUEUE = 'text-to-speech'
    MAX_MESSAGE_LENGTH = 150
    VOLUME = 200
    WORDS_PER_MINUTE = 155

    def validate_message(self, message):
        if 'text' not in message:
            return False

        # Refuse to play back messages which are too long.
        if len(message['text']) > self.MAX_MESSAGE_LENGTH:
            return False

        return True

    def process_message(self, message):
        """ The implementation is very simple - call the (e)speak command line
            utility with the correct parameters. """

        self.logger.info("Received request to synth voice for text: %s" %
                         message['text'])

        params = {
            'wpm': self.WORDS_PER_MINUTE,
            'volume': self.VOLUME,
            'text': message['text']
        }
        cmd_line = "espeak -s %(wpm)s -a %(volume)s \"%(text)s\"" % params
        os.system(cmd_line)
        self.logger.info("Executed command %s" % cmd_line)

if __name__ == "__main__":
    setup_logging()
    module = TextToSpeech()
    module.run()
