import os
import sys
import subprocess
from flask import Flask
from flask import jsonify
import utils.times as times
from utils.input import Input
from utils.config import Config

class Sender:
    
    def __init__(self, config):
        self.app = Flask(__name__)
        self.config = config
        self.socket_test_server = None
        self.send_timestamp = None
    
    def start_cmd(self):
        # directed led
        #start = 'insmod send_light_kernel.ko action=send device=high time_base_unit=130000 data='"abcdefghijklmnopqrstuvwxyz0123456789"''
        # pervasive led
        start = 'insmod send_light_kernel.ko action=send device=high time_base_unit=50000 data='"abcdefghijklmnopqrstuvwxyz0123456789"''
        result = subprocess.call(start, shell=True)
        self.send_timestamp = times.get_timestamp()
        if result == 0:
            return jsonify(result=True)
        else:
            return jsonify(result=False)
    
    def stop_cmd(self):
        stop = "rmmod send_light_kernel"
        result = subprocess.call(stop, shell=True)
        if result == 0:
            return jsonify(result=True)
        else:
            return jsonify(result=False)
    
    def timestamp(self):
        return jsonify(result=self.send_timestamp)
    
    def register_endpoints(self):
        self.app.add_url_rule("/start_cmd", "start_cmd", self.start_cmd, methods=['GET', 'POST'])
        self.app.add_url_rule("/stop_cmd", "stop_cmd", self.stop_cmd, methods=['GET', 'POST'])
        self.app.add_url_rule("/timestamp", "timestamp", self.timestamp, methods=['GET', 'POST'])
    
    def start(self):
        self.register_endpoints()
        self.app.run(host="0.0.0.0", port=int(self.config.get("Sender port")))

def main():
    if len(sys.argv) != 2:
        sys.exit("Wrong number of input parameters\n")
    Input(sys.argv)
    path = os.path.dirname(__file__)
    config = Config(path, "Remote Board")
    sender = Sender(config)
    sender.start()
    
if __name__ == "__main__":
    main()
