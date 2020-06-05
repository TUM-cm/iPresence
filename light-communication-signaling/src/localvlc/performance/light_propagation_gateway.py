from flask import Flask, jsonify, request
from localvlc.performance.metrics import VlcMetrics
from receive_light.light_control import ReceiveLightControl

app = Flask(__name__)

def morse(period, template):
    evaluator = VlcMetrics()
    action = ReceiveLightControl.Action.evaluate_morse
    connector = ReceiveLightControl.Connector.local
    light_control = ReceiveLightControl(action, conn=connector, evaluator=evaluator,
                                        evaluate_period=period, evaluate_template=template,
                                        evaluate_throughput=True, evaluate_error=True)
    light_control.start()
    return evaluator

# http://192.168.2.102:11234/evaluation_morse?template=abcdefghijklmnopqrstuvwxyz0123456789&period=2 
@app.route('/evaluation_morse')
def evaluation_morse():
    template = request.args.get('template')
    period = int(request.args.get('period'))
    evaluator = morse(period, template)
    return jsonify(result=evaluator.get_error()[0])

def manchester(period, template, ip, port):
    evaluator = VlcMetrics()
    action = ReceiveLightControl.Action.evaluate_manchester
    connector = ReceiveLightControl.Connector.socket
    light_control = ReceiveLightControl(action, conn=connector, evaluator=evaluator,
                                        evaluate_period=period, evaluate_template=template,
                                        evaluate_ip=ip, evaluate_port=port,
                                        evaluate_throughput=True, evaluate_error=True)
    light_control.start()
    return evaluator

# http://192.168.2.102:11234/evaluation_manchester?template=abcdefghijklmnopqrstuvwxyz0123456789&period=2&ip=192.168.0.1&port=11234
@app.route('/evaluation_manchester')
def evaluation_manchester():
    template = request.args.get('template')
    period = int(request.args.get('period'))
    ip_server = request.args.get('ip')
    port_server = int(request.args.get('port'))
    evaluator = manchester(period, template, ip_server, port_server)
    return jsonify(result=evaluator.get_error()[0])

app.run(host="0.0.0.0", port=11234)
