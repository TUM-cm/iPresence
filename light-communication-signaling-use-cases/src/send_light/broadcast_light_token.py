import sched
import time
import threading
import logging
from crypto.otp import OneTimePass
from send_light_user import LightSender

def str_to_bool(s):
    if s == 'True':
        return True
    else:
        return False

class BroadcastLightToken(object):
    
    def __init__(self, kernel_module, time_base_unit, token_period=30,
                 token_num=None, evaluate=False, callback=None):
        self.token_period = int(token_period)
        self.evaluate = str_to_bool(evaluate)
        self.token_num = int(token_num)
        self.callback = callback
        self.light_sender = LightSender(kernel_module, time_base_unit=time_base_unit)
        self.totp = OneTimePass(interval=self.token_period)
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.priority = 1
        self.token = None
        self.token_counter = 0
        self.broadcast_event = None
    
    def start_transmission(self):
        self.token = self.totp.get_token()
        self.light_sender.set_data(self.get_token())
        self.light_sender.start()
        logging.info(str(time.time()) + " : " + self.token)
        if self.evaluate:
            self.token_counter += 1
            logging.info("token counter: " + str(self.token_counter))
    
    def broadcast_light_token(self):
        self.light_sender.stop()
        if self.evaluate:
            if self.token_counter != self.token_num:
                self.restart_broadcast()
        else:
            self.restart_broadcast()
    
    def restart_broadcast(self):
        self.start_transmission()
        self.broadcast_event = self.scheduler.enter(self.token_period,
                                                    self.priority,
                                                    self.broadcast_light_token, ())
    
    def __start_send(self):
        self.start_transmission()
        self.scheduler.enter(self.token_period, self.priority, self.broadcast_light_token, ())    
        self.scheduler.run()
    
    def start(self):
        thread = threading.Thread(target=self.__start_send, args=())
        thread.start()
    
    def get_token(self):
        return self.token
