import copy
import socket

import requests

from core import PDU

class IPPower(PDU):
    """ PDU that routes incoming measurements from sensors to the
        actual processing pipelines """

    QUEUE = 'ip-power'
    DEFAULT_USER = 'admin'
    DEFAULT_PASSWORD = '12345678'

    def process_message(self, message):
        
        """ Prepare parameters for HTTP request """
        params = copy.deepcopy(message)
        # cmd -> state conversion
        cmd = params['cmd'].lower()
        params['state'] = {'on': 0, 'off': 1}[cmd]
        del params['cmd']
        # Fill in default user & password if they aren't provided
        params['user'] = params.get('user', self.DEFAULT_USER)
        params['password'] = params.get('password', self.DEFAULT_PASSWORD)
        
        url = "http://%(ip)s/Set.cmd?CMD=SetPower+P6%(output)s=%(state)s" % params
        r = requests.get(url, auth=(params['user'], params['password']))
        
        if (r.status_code != 200):
            self.log("HTTP request failed with status code %d and response " % 
                     r.status_code, r.text)
        
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
        return int(message['output']) in range (1, 4)
    
    def check_ip(self, message):
        try:
            socket.inet_aton(message['ip'])
            return True
        except socket.error:
            return False
    
if __name__ == "__main__":
    module = IPPower(debug = True)
    module.run()
