

class Matcher(object):
    
    def __init__(self, value, accessor):
        ''' Matches a constant value against an accessor'''
        self._value = value
        self._accessor = accessor
        
    def __eq__(self, other):
        return self._value == self._accessor(other)

