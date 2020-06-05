import os
from utils.serializer import DillSerializer
from localvlc.testbed_setting import Testbed
from localvlc.energy import EnergyMeasurements
from localvlc.performance.metrics import VlcMetrics
from receive_light.light_control import ReceiveLightControl

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def test_energy_morse_parameter(conversion_to_nanosecond=1000):
    pervasive_led_sampling_intervals = [10, 20, 30]
    #directional_led_sampling_intervals = [20, 30, 50]
    sampling_interval = pervasive_led_sampling_intervals[0] * conversion_to_nanosecond
    print("sampling interval: ", sampling_interval)
    light_control = ReceiveLightControl(ReceiveLightControl.Action.data_amount_morse,
                                        sampling_interval=sampling_interval)
    light_control.start()

def test_energy_encryption(led, morse, eval_ip="192.168.0.2", eval_port=11234, speck=False, aes=False):
    if morse:
        light_control = ReceiveLightControl(
            ReceiveLightControl.Action.data_amount_morse, sampling_interval=led.get_sampling_interval())
    else:
        if speck:
            action = ReceiveLightControl.Action.data_amount_manchester_speck
        elif aes:
            action = ReceiveLightControl.Action.data_amount_manchester_aes  
        else:
            action = ReceiveLightControl.Action.data_amount_manchester
        light_control = ReceiveLightControl(
            action, conn=ReceiveLightControl.Connector.socket, evaluate_ip=eval_ip, evaluate_port=eval_port)    
    light_control.start()

def evaluate_morse(led, test_rounds, test_period):
    data_len = 1024
    error = True
    latency = False
    throughput = True
    evaluator = VlcMetrics()
    path = os.path.join(
        __location__, "..", "results", "error_data_len", led.get_name(), "data_len_" + str(data_len))
    test_data = "abcdefghijklmnopqrstuvwxyz0123456789"
    while evaluator.get_data_rounds() < test_rounds:
        print("evaluation round: ", evaluator.get_data_rounds())
        conn = ReceiveLightControl.Connector.local
        action = ReceiveLightControl.Action.evaluate_morse
        light_control = ReceiveLightControl(action, conn=conn,
                                            evaluator=evaluator,
                                            evaluate_period=test_period,
                                            evaluate_template=test_data,
                                            evaluate_error=error,
                                            evaluate_latency=latency,
                                            evaluate_throughput=throughput,
                                            sampling_interval=led.get_sampling_interval())
        light_control.start()
        print("-------------------")
    evaluator.check_data()
    evaluator.print_data()
    serializer = DillSerializer(path)
    serializer.serialize(evaluator)

def test_single_throughput(led, test_data, test_rounds):
    evaluator = VlcMetrics()
    while evaluator.get_data_rounds() < test_rounds:
        print("evaluation round: ", evaluator.get_data_rounds())
        action = ReceiveLightControl.Action.evaluate_morse
        conn = ReceiveLightControl.Connector.local
        light_control = ReceiveLightControl(action, conn=conn, evaluator=evaluator,
                                            evaluate_period=10,
                                            #evaluate_data_amount=file_size,
                                            evaluate_template=test_data,
                                            evaluate_throughput=True,
                                            evaluate_error=True,
                                            #evaluate_latency=latency,
                                            sampling_interval=led.get_sampling_interval(),
                                            #evaluate_ip=ip, evaluate_port=port
                                            )
        light_control.start()
    evaluator.check_data()
    evaluator.print_data()

def test_parse_morse(led):
    light_control = ReceiveLightControl(ReceiveLightControl.Action.parse_morse,
                                        sampling_interval=led.get_sampling_interval())
    light_control.start()

def test_parse_manchester():
    light_control = ReceiveLightControl(ReceiveLightControl.Action.parse_manchester,
                                        conn=ReceiveLightControl.Connector.socket,
                                        evaluate_ip="192.168.0.2", evaluate_port=11234)
    light_control.start()
    
'''
insmod vlc.ko for sender and receiver
python -m localvlc.performance.socket_test_server (with udp)
python -m receive_light.light_control
''' 
def evaluate_comparison(led, test_rounds, test_period, test_data,
                        morse=True, throughput=True, error=True, latency=False,
                        manchester_ip="192.168.0.2", manchester_port=11234):
    basedir_results = os.path.join(__location__, "..", "results", "vlc-performance")
    # 1400 B/s throughput from previous evaluation for best working VLC parameters
    # 1 kb = 0.7 s > 10 s
    # 5 kB = 3.7 s > 40 s
    # 10 kB = 7.3 s > 1 min.
    # 100 kB = 73 s (1,20 min.) > 12 min.
    # 200 kB = 146 s (2,5 min.) > 25 min.
    # 500 kB = 365 s = (6 min.) > 60 min.
    file_sizes = [1024, 5120, 10240, 102400] # 512000
    energy_measurements = EnergyMeasurements()
    for file_size in file_sizes:
        print("file size: ", file_size)
        evaluator = VlcMetrics()
        while evaluator.get_data_rounds() < test_rounds:
            print("evaluation round: ", evaluator.get_data_rounds())
            if morse:
                action = ReceiveLightControl.Action.evaluate_morse
                conn = ReceiveLightControl.Connector.local
                data_encoding = "morse"
            else:
                action = ReceiveLightControl.Action.evaluate_manchester
                conn = ReceiveLightControl.Connector.socket
                data_encoding = "manchester"
            
            print("start energy measurements")
            energy_measurements.start_periodic_sampling()
            print("start evaluation")
            light_control = ReceiveLightControl(action, conn=conn, evaluator=evaluator,
                                                evaluate_period=test_period,
                                                evaluate_data_amount=file_size,
                                                evaluate_template=test_data,
                                                evaluate_throughput=throughput,
                                                evaluate_error=error,
                                                evaluate_latency=latency,
                                                sampling_interval=led.get_sampling_interval(),
                                                evaluate_ip=manchester_ip, evaluate_port=manchester_port)
            light_control.start()
            print("stop energy measurements")
            energy_measurements.stop_periodic_sampling()
            data_period = evaluator.get_data_period()[-1]
            data_amount = evaluator.get_throughput_total()[-1]
            print("data amount: ", data_amount)
            print("data period: ", data_period)
            energy_mJ = energy_measurements.calculate_energy(data_period)
            evaluator.energy(energy_mJ)
            energy_measurements.reset()    
            print("stop evaluation")
        evaluator.check_data()
        evaluator.print_data()
        filename = "%s-file-size-%d" % (data_encoding, file_size)
        serializer = DillSerializer(os.path.join(basedir_results, filename))
        serializer.serialize(evaluator)
        print("---------------------------------")
    energy_measurements.closeDevice()
    
def evaluate_vlc_parameters(test_rounds, test_period, test_data, morse=True,
                            throughput=True, error=True, latency=False,
                            manchester_ip="192.168.0.2", manchester_port=11234):
    basedir_results = os.path.join(__location__, "..", "results", "vlc_parameters")
    time_base_unit = 50000
    sampling_intervals = [5000, 10000, 15000, 20000, 25000, 30000, 50000, 100000, 150000] # ns
    # 5000, 10000, 15000, 20000, 25000, 30000, 50000, 100000, 150000 # pervasive LED
    # 100000, 110000, 120000, 130000, 140000, 150000 # directed LED
    for sampling_interval in sampling_intervals:
        if morse:
            print("sampling interval: ", sampling_interval)    
        evaluator = VlcMetrics()
        while evaluator.get_data_rounds() < test_rounds:
            print("evaluation round: ", evaluator.get_data_rounds())
            if morse:
                action = ReceiveLightControl.Action.evaluate_morse
                conn = ReceiveLightControl.Connector.local
                data_encoding = "morse"
            else:
                action = ReceiveLightControl.Action.evaluate_manchester
                conn = ReceiveLightControl.Connector.socket
                data_encoding = "manchester"
            print("start evaluation")
            light_control = ReceiveLightControl(action, conn=conn, evaluator=evaluator,
                                                evaluate_period=test_period,    
                                                evaluate_template=test_data,
                                                evaluate_throughput=throughput,
                                                evaluate_error=error,
                                                evaluate_latency=latency,
                                                sampling_interval=sampling_interval,
                                                evaluate_ip=manchester_ip, evaluate_port=manchester_port)
            light_control.start()
            print("stop evaluation")
        evaluator.check_data()
        evaluator.print_data()
        if morse:
            filename = "%s_sampling_%d_time_base_unit_%d"
            filename = filename % (data_encoding, sampling_interval, time_base_unit)
        else:
            filename = "%s_freq_%d"
            filename = filename % (data_encoding)
        serializer = DillSerializer(basedir_results + filename)
        serializer.serialize(evaluator)
        print("---------------------------------")
    
def test_light_propagation(led, test_rounds, test_period, test_data, measurement_point):
    result_file = "../results/signal_propagation/light"
    object_serializer = DillSerializer(result_file)
    evaluation_result = object_serializer.deserialize() if os.path.isfile(result_file) else dict()
    action = ReceiveLightControl.Action.evaluate_morse
    conn = ReceiveLightControl.Connector.local
    vlc_metrics = VlcMetrics()
    while vlc_metrics.get_data_rounds() < test_rounds:
        print("evaluation round: ", vlc_metrics.get_data_rounds())
        light_control = ReceiveLightControl(action, conn=conn, evaluator=vlc_metrics,
                                            evaluate_period=test_period, evaluate_template=test_data,
                                            evaluate_throughput=True, evaluate_error=True,
                                            sampling_interval=led.get_sampling_interval())
        light_control.start()
    vlc_metrics.check_data()
    evaluation_result[measurement_point] = vlc_metrics
    object_serializer.serialize(evaluation_result)

if __name__ == "__main__":
    led = Testbed.Pervasive_LED
    test_data = "abcdefghijklmnopqrstuvwxyz0123456789"
    test_rounds = 10
    test_period = 10
    morse = True
    
    #measurement_point = 6
    #test_light_propagation(led, test_rounds, test_period, test_data, measurement_point)
    #test_parse_manchester()
    #test_single_throughput(led, test_data, test_rounds)
    #evaluate_morse(led, test_rounds, test_period)
    #test_parse_morse(led)
    #test_energy_encryption(led, morse, aes=True) # speck, aes
    #test_energy_morse_parameter()
    #evaluate_vlc_parameters(test_rounds, test_period, test_data, morse)

    #('duration (s): ', 192.61190986633301)
    #('mean current (mA): ', 369.91192996620845)
    #('mean voltage (V): ', 4.9932499999999997)
    #('power (W): ', 1.8470656383879225)
    #('energy (mWh): ', 98.823967450916513)
    
    #print("measure baseline current")
    #energy_measurements = EnergyMeasurements()
    #baseline_current = energy_measurements.measure_baseline()
    #energy_measurements.measure_baseline_periodic()
    
    evaluate_comparison(led, test_rounds, test_period, test_data, morse)
    