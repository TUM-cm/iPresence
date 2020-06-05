import os
import glob
import numpy
import random
import string
import utils.kernel_module as kernel_module
from utils.serializer import DillSerializer
from send_light.send_light_user import LightSender
from localvlc.testbed_setting import Testbed

sender = False

def bit_error_ratio(result, template):
    byte_diff = 0
    result = "".join(result.split())
    template = "".join(template.split())
    for char1, char2 in zip(result, template):
        if char1 != char2:
            byte_diff += 1
    data_len = min(len(result), len(template))
    return byte_diff / data_len

def main():
    if sender:
        kernel_module.remove(kernel_module.SEND_KERNEL_MODULE)
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_len = 5 # 5, 10, 50, 100, 150, 200, 300, 400, 500, 700, 900, 1024
        led = Testbed.Pervasive_LED
        path = os.path.join(__location__, "..", "..", "localvlc", "results",                        
                            "error_data_len", led.get_name(), "groundtruth_data_len_" + str(data_len))
        test_string = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(data_len))
        light_sender = LightSender()
        light_sender.set_data(test_string)
        light_sender.set_time_base_unit(led.get_time_base_unit())
        light_sender.start()
        serializer = DillSerializer(path)
        serializer.serialize(test_string)
    else:
        leds = ["directed_led", "pervasive_led"]
        base_path = "../results/error_data_len/"
        for led in leds:
            print("led: ", led)
            path_groundtruth = os.path.join(base_path, led, "groundtruth_data_len_*")
            for path_groundtruth in glob.glob(path_groundtruth):
                data_len = path_groundtruth.split("_")[-1]
                path_raw_data = os.path.join(base_path, led, "data_len_" + data_len)
                groundtruth = DillSerializer(path_groundtruth).deserialize()
                raw_data = DillSerializer(path_raw_data).deserialize().raw_data
                count = 0
                result = list()
                for series in raw_data:
                    for msg in series:
                        count += 1        
                        result.append(bit_error_ratio(msg, groundtruth))
                print("data len: ", len(groundtruth))
                print("count: ", count)
                #print("groundtruth: ", groundtruth)
                #print("raw data: ", raw_data[0][0])
                print("bit error ratio: ", numpy.mean(result))
                print("max bit error ratio: ", numpy.max(result))
                print("---")
            print("###")
    
if __name__ == "__main__":
    main()
