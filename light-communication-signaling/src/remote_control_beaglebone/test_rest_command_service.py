import requests
import json

url = "http://localhost:11234/"

def print_request(r):
    print r.url
    print r.text

def test_command_api():
    endpoint = "api/command"
    rest_api = url + endpoint
    header = {"Content-type": "application/json"}
    #payload = { "command": "ls -la" }
    payload = { "command": "./executable/hello.exe" }
    r = requests.post(rest_api, data=json.dumps(payload), headers=header)
    print_request(r)

test_command_api()
