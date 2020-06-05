import requests
import json
from utils.custom_enum import enum_name

class ControlSender(object):
    
    Evaluation = enum_name("morse_code", "manchester_code")
    
    def __init__(self, config):
        self.url = config.get("Sender protocol") + config.get("Sender ip") + ":" + config.get("Sender port") + "/"
    
    def start_cmd(self):
        r = requests.get(self.url + "start_cmd")
        data = json.loads(r.text)
        return data["result"]
    
    def stop_cmd(self):
        r = requests.get(self.url + "stop_cmd")
        data = json.loads(r.text)
        return data["result"]
    
    def get_send_timestamp(self):
        r = requests.get(self.url + "timestamp")
        data = json.loads(r.text)
        return data["result"]  
