import threading
from utils.vlc_interfaces import SenderDevice
from send_light.light_beacon import LedAction
from send_light.light_beacon import LightBeacon
from receive_light.connector_mqtt import MqttConnector
from receive_light.light_control import ReceiveLightControl

def run_impulse_response():
    '''
    light_control = ReceiveLightControl(ReceiveLightControl.Action.stream_raw_light_signal,
                                        conn=ReceiveLightControl.Connector.mqtt,
                                        mqtt_remote_ip="131.159.24.85",
                                        mqtt_data_format=MqttConnector.FORMAT_VOLTAGE)
    light_control.start()
    '''
    
    evaluate_period = 10
    remote_light_sensing = []
    remote_light_emitting = []
    path_evaluation_data = "../evaluation/results/impulse_response/voltage_"
    led_actions = [LedAction(2, SenderDevice.high, 0.1),
                      LedAction(5, SenderDevice.high, 0.5),
                      LedAction(7, SenderDevice.high, 1)]
    
    #remote_nodes = [("192.168.7.2", "01.05.038_desk", led_actions), ("131.159.24.85", "01.05.038_window", None)]
    remote_nodes = [("beaglebone.local", "home", led_actions)]
    for ip, description, led_action in remote_nodes:
        light_control = ReceiveLightControl(ReceiveLightControl.Action.serialize_raw_light_signal,
                                            data_path_voltage=path_evaluation_data + description,
                                            evaluate_period=evaluate_period,
                                            conn=ReceiveLightControl.Connector.mqtt,
                                            mqtt_remote_ip=ip,
                                            mqtt_data_format=MqttConnector.FORMAT_VOLTAGE)
        remote_light_sensing.append(threading.Thread(target=light_control.start))
        light_beacon = LightBeacon(ip)
        if led_action:
            for action in led_action:
                light_beacon.add(action.get_delay(), action.get_cmd())
        remote_light_emitting.append(threading.Thread(target=light_beacon.start))
    
    # remote sensing
    for remote_sensing, remote_lighting in zip(remote_light_sensing, remote_light_emitting):
        remote_sensing.start()
        remote_lighting.start()
    
    for remote_sensing, remote_lighting in zip(remote_light_sensing, remote_light_emitting):
        remote_sensing.join()
        remote_lighting.join()

def main():
    run_impulse_response()

if __name__ == "__main__":
    main()