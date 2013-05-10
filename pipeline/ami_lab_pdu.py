from core import settings
from core import PDU
from lib import sessions_store

class AmILabPDU(PDU):
    """ 
    PDU enhanced with features useful for AmILab needs
    """

    TRAJECTORIES_QUEUE = 'trajectories'
    
    def __init__(self, **kwargs):
        super(AmILabPDU, self).__init__(**kwargs)
        self.sessions_store = sessions_store.SessionsStore(settings.REDIS_RAW_SESSIONS_DB)
                
    def add_to_session_store(self, sid, time, mappings):
        """ 
        Adds some data to a session. It also sends a notification to trajectories pdu via the message queue
        """ 
        self.sessions_store.set(sid, time, mappings)
        self.send_to(self.TRAJECTORIES_QUEUE, {'sid': sid, 'time': time, 'value': mappings})
