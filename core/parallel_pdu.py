from multiprocessing import Pool
import logging

from lib.atomic_int import AtomicInt
from pdu import PDU

logger = logging.getLogger(__name__)

def run_and_return(f, param, k, v):
    """ Runs function f(param) and returns a dictionary containing {k:v}
        and the result of the function run. """
    f_result = f(param)
    to_return = {'result': f_result}
    to_return[k] = v
    return to_return

class ParallelPDU(PDU):
    """ PDU which can process messages in parallel. In order to
        be able to do this, message processing is broken into
        two parts:

        - heavy_preprocess(msg) - this is the actual part that will be
          parallelized. This will be executed on a multiprocess pool (so
          we can do both CPU bound and I/O bound, but at the expense of
          having to pass the heavy_preprocess function as a parameter
          because it must be picklable and thus unbound).

        - light_postprocess(msg) - this is the actual part that will executed
          sequentially - after each heavy processing is done in parallel,
          this processing will be done in serial.

        This kind of PDU also has 2 configuration options:

            ORDERED_DELIVERY = True/False => light_postprocess will be executed
                    in the same order as the messages coming into the PDU.
                    This means a lower throughput (because the thread pool
                    might finish messages which came in later early) at the
                    expense of ordered delivery when it's needed.

            POOL_SIZE = N (default 4). The size of the pool. Usually it's
                    recommended in operating system literature to set this
                    to the number of cores for CPU bound tasks and to
                    2 x number of cores for I/O bound tasks.
    """

    ORDERED_DELIVERY = False
    POOL_SIZE = 4
    UNFINISHED_TASKS_THRESHOLD = 2 * POOL_SIZE

    def __init__(self, **kwargs):
        super(ParallelPDU, self).__init__(**kwargs)
        # We need to have the heavy preprocess function given to us
        # as a parameter. This is because python 2.7 multiprocess can't
        # pickle bound functions, thus cannot run them in parallel processes.
        if not 'heavy_preprocess' in kwargs:
            raise ValueError('Need a heavy_preprocess function')
        self.heavy_preprocess = kwargs['heavy_preprocess']

        self.pool = Pool(self.POOL_SIZE)

        # Generate a unique sequence number for each message
        self.message_no = 0
        # Sequence number of last postprocessed message for ordered delivery
        self.last_postprocessed_message_no = 0

        # seq no to preprocess result mapping
        self.preprocess_results = {}
        # seq no to message mapping
        self.messages = {}

        self.unfinished_tasks = AtomicInt()
        
        self.last_busy_result = False

    def light_postprocess(self, preprocess_result, message):
        raise NotImplemented("Please implement this in your sub-class!")

    def _internal_light_postprocess(self, result):
        """ This function acts as a callback for when a task given to
            the thread pool (aka a heavy_preprocess) is finished,
            in order to decide what to do next. """

        self.unfinished_tasks.dec()

        message_no = result['message_no']
        actual_result = result['result']

        # If we have ordered delivery, we register the result
        # and check if the next message to process has arrived.
        # If it does, keep processing until we're out of messages.
        if self.ORDERED_DELIVERY:
            self.preprocess_results[message_no] = actual_result
            next_message = self.last_postprocessed_message_no + 1
            while next_message in self.preprocess_results:
                actual_result = self.preprocess_results.pop(next_message)
                message = self.messages.pop(next_message)
                self.light_postprocess(actual_result, message)
                self.last_postprocessed_message_no = next_message
                next_message = self.last_postprocessed_message_no + 1
        # Otherwise, we don't care about the order, and we process
        # the finished message immediately.
        else:
            message = self.messages.pop(message_no)
            self.light_postprocess(actual_result, message)

    def busy(self):
        """ By default, a parallel PDU is busy if it has at least
            UNFINISHED_TASKS_THRESHOLD tasks which have not finished
            yet.
        """
        unfinished_tasks = self.unfinished_tasks.get()
        result = unfinished_tasks > self.UNFINISHED_TASKS_THRESHOLD
        if result and not self.last_busy_result:            
            self.log("Busy with %d unfinished tasks!" % unfinished_tasks)
        
        self.last_busy_result = result
        return result

    def process_message(self, message):
        """ Message processing will be done in 2 steps:

            - give the message a unique ID and enqueue this for processing
                in parallel
            - when a job is done, we have 2 cases:
                - on ordered delivery, process the next streak of jobs
                    which are consecutive and have no unfinished job before
                    them
                - on normal delivery, process the actual job
        """
        self.unfinished_tasks.inc()

        # Give the message a unique number and keep track of it.
        self.message_no = self.message_no + 1
        self.messages[self.message_no] = message

        # Run heavy_process, which is an unbound function on the thread pool.
        # The explanation is that Python isn't good at pickling bound functions
        # (soon to be improved in Python 3.3), so it requires us to run an
        # unbound function on the thread pool.
        self.pool.apply_async(run_and_return,
                              [self.heavy_preprocess, message,\
                               'message_no', self.message_no],
                              callback = self._internal_light_postprocess)
