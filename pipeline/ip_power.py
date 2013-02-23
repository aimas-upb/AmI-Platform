import copy
import socket

import requests

from core import PDU
from lib.log import setup_logging


class IPPower(PDU):
    """ PDU that routes incoming measurements from sensors to the
        actual processing pipelines """

    QUEUE = 'ip-power'
    DEFAULT_USER = 'admin'
    DEFAULT_PASSWORD = '12345678'

    def process_message(self, message):
        self.logger.info("Received message: %r" % message)

        """ Prepare parameters for HTTP request """
        params = copy.deepcopy(message)

        # Convert command to state value
        params['state'] = {'on': 0, 'off': 1}[params.pop('cmd').lower()]

        # Fill in default user & password if they aren't provided
        params['user'] = params.get('user', self.DEFAULT_USER)
        params['password'] = params.get('password', self.DEFAULT_PASSWORD)
        self.logger.info("Will perform HTTP request using params %r" % params)

        url = "http://%(ip)s/Set.cmd?CMD=SetPower+P6%(output)s=%(state)s" %\
                params
        self.logger.info("Performing HTTP request to URL %s" % url)

        # Make the actual request and log the result
        r = requests.get(url, auth=(params['user'], params['password']))
        if (r.status_code != 200):
            self.logger.info("HTTP request failed with status code %d "
                             "and response " % r.status_code, r.text)
        else:
            self.logger.info("Everything went allright in communication with "
                             "IP power equipment")

    def validate_message(self, message):
        for required_key in ['cmd', 'output', 'ip']:
            if not required_key in message:
                return False

        return  self.check_cmd(message) and \
                self.check_output(message) and \
                self.check_ip(message)

    def check_cmd(self, message):
        return message['cmd'].lower() in ["on", "off"]

    def check_output(self, message):
        try:
            int(message['output'])
        except:
            return False
        return int(message['output']) in range(1, 4)

    def check_ip(self, message):
        try:
            socket.inet_aton(message['ip'])
            return True
        except socket.error:
            return False

if __name__ == "__main__":
    setup_logging()
    module = IPPower(debug=True)
    module.run()
