import sys
import os
import subprocess
from flask import Flask
from flask import jsonify
from flask import request
from flask.views import MethodView
from utils.input import Input
from utils.config import Config

class Webserver(object):
    
    def __init__(self):
        path = os.path.dirname(__file__)
        self.app = Flask(__name__)
        self.webserver = Config(path, "Webserver")
        self.command_api = Config(path, "Endpoint: Command")
    
    def register_endpoints(self):
        command_view = Command.as_view(self.command_api.get("name"))
        self.app.add_url_rule(self.command_api.get("default"), view_func=command_view)
    
    def start(self):
        self.register_endpoints()
        if self.webserver.get("tls") == "True":
            self.app.run(host=self.webserver.get("address"),
                         port=int(self.webserver.get("port")),
                         ssl_context=(self.webserver.get("certificate"),
                                      self.webserver.get("key")))
        else:
            self.app.run(host=self.webserver.get("address"),
                         port=int(self.webserver.get("port")))

class Command(MethodView):
    
    def post(self):
        if request.is_json:
            data = request.get_json(silent=True)
            try:
                #command = data["command"].split()
                command = data["command"]
                result = subprocess.call(command)
                return jsonify(result)
                #output = subprocess.check_output(command)
                #return jsonify(output)
            except:
                return jsonify(False)
        else:
            return jsonify(False)

def main():
    if len(sys.argv) != 2:
        sys.exit("\Number of input parameters wrong\n")
    Input(sys.argv)
    webserver = Webserver()
    webserver.start()
    
if __name__ == "__main__":
    main()