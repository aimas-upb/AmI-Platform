from core import PDU
from lib.log import setup_logging
from lib.processed_session_store import ProcessedSessionStore

class SessionProcessor(PDU):
    """ Module which receives notifications that a new measurement is added
    to a trajectory. It searches for a nearby trajectory in the processed
    sessions DB, and if none is found, creates a new one.

    Search is done via spatial & temporal criteria.
    """

    QUEUE = 'session_processor'

    def __init__(self, **kwargs):
        super(SessionProcessor, self).__init__(**kwargs)
        self.processed_session_store = ProcessedSessionStore()

    def process_message(self, message):

        # NOTE: we're passing the session_id as well because we have session
        # affinity: once a measurement from a "source" session is declared to
        # be part of a "destination" session, all subsequent measurements will
        # go to the same session.
        dst_session_id = self.processed_session_store.session_ending_at(message)

        # If no closely matching session is found, create a new one
        if dst_session_id is None:
            dst_session_id = self.processed_session_store.new_session_id()

        # Write the measurement to the "closest" matching destination session
        self.processed_session_store.set(sid=dst_session_id,
                                         timestamp=message['time'],
                                         info=message['info'])

if __name__ == "__main__":
    setup_logging()
    module = SessionProcessor()
    module.run()
