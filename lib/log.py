import logging
import sys

def setup_logging(**kwargs):
    """ Sets up logging to standard output for a PDU """
    params = {
              'level': logging.INFO,
              'stream': sys.stdout,
              'format': "[%(asctime)s] - [%(process)d * %(thread)d] %(module)s.%(filename)s:%(funcName)s:%(lineno)d - %(message)s"}
    params.update(kwargs)
    logging.basicConfig(**params)
