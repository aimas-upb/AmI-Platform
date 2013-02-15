import logging


def setup_logging():
    """ Sets up logging to standard output for a PDU """
    logging.basicConfig(level=logging.INFO)
