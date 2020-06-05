import threading

class FuncThread(threading.Thread):
    
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        self._stop_event = threading.Event()
        threading.Thread.__init__(self)
    
    def run(self):
        while not self.stopped():
            self._target(*self._args)
    
    def stop(self):
        self._stop_event.set()
    
    def stopped(self):
        return self._stop_event.is_set()
