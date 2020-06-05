import os
import sys
from utils.config import Config
from utils.input import Input
from utils.serializer import DillSerializer
from localvlc.performance.metrics import VlcMetrics
from localvlc.performance.control_sender import ControlSender
from receive_light.light_control import ReceiveLightControl

if len(sys.argv) != 2:
        sys.exit("Wrong number of input parameters\n")
Input(sys.argv)
path = os.path.dirname(__file__)
config = Config(path, "Remote Board")
control_sender = ControlSender(config)

repeat = 0
evaluator = VlcMetrics()
rounds = 10
result_path = "../results/vlc_latency/"

def received_msg(receive_timestamp):
    global repeat
    send_timestamp = control_sender.get_send_timestamp()
    print "send timestamp"
    print send_timestamp
    print "-------------------"    
    evaluator.latency(send_timestamp, receive_timestamp)
    control_sender.stop_cmd()
    evaluator.print_data()    
    repeat += 1    
    print "##############################"    
    print "repeat: ", repeat
    print "##############################"    
    if repeat < rounds:
        start_latency()
    else:
        serializer = DillSerializer(result_path + "latency")
        serializer.serialize(evaluator)

def start_latency():
    global send_timestamp
    #sampling_interval = 50000 # directed led
    sampling_interval = 30000 # pervasive led
    latency = True
    test_data = "abcdefghijklmnopqrstuvwxyz0123456789"
    action = ReceiveLightControl.Action.evaluate_morse
    conn = ReceiveLightControl.Connector.local
    light_control = ReceiveLightControl(action, conn=conn,
                                        evaluate_template=test_data,
                                        evaluate_latency=latency,
                                        callback_latency=received_msg,
                                        sampling_interval=sampling_interval)
    light_control.start()
    control_sender.start_cmd()

def main():
    start_latency()

if __name__ == "__main__":
    main()
