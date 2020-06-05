
class AuthorizationResult(object):
    
    def __init__(self, start, stop, duration, result):
        self.start = start
        self.stop = stop
        self.duration = duration
        self.result = result
    
    def get_start(self):
        return self.start
    
    def get_stop(self):
        return self.stop
    
    def get_duration(self):
        return self.duration
    
    def get_result(self):
        return self.result
