import logging


def setup_logging():
    """ Sets up logging to standard output for a PDU """
    logging.basicConfig(level=logging.INFO,
                        format="[%(asctime)s] - [%(process)d * %(thread)d] %(filename)s:%(funcName)s:%(lineno)d - %(message)s")
