import threading

class AtomicInt(object):

    def __init__(self, initial_value = 0):
        self.lock = threading.Lock()
        self.count = initial_value

    def inc(self):
        return self._run_with_lock(self.__inc)

    def dec(self):
        return self._run_with_lock(self.__dec)

    def get(self):
        return self._run_with_lock(lambda: self.count)

    def _run_with_lock(self, f):
        """ Run f while acquiring self.lock. """
        self.lock.acquire()
        try:
            return f()
        finally:
            self.lock.release()

    def __inc(self):
        self.count += 1
        return self.count

    def __dec(self):
        self.count -= 1
        return self.count