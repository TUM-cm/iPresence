import os
import glob
import numpy
from error_rate_data_len import bit_error_ratio
from utils.serializer import DillSerializer

def overall_bit_error_ratio(raw_data, groundtruth):
    result = list()
    for series in raw_data:
        for msg in series:
            result.append(bit_error_ratio(msg, groundtruth))
    return numpy.mean(result)

def main():
    base_path = "../results/vlc_window_glass_light_power/"
    with_glass = os.path.join(base_path, "*_with")
    
    groundtruth = dict()
    groundtruth["1w"] = "abcdefghijklmnopqrstuvwxyz0123456789"
    groundtruth["15w"] = "abcdefghijklmnopqrstuvwxyz0123456789"
    groundtruth["2w"] = "abcdefghijklmnopqrstuvwxyz0123456789"
    groundtruth["3w"] = "abcdefghijklmnopqrstuvwxyz0123456789"
    groundtruth["4w"] = "tbcdefghijklmnopqrstuvwxyz0123456789"
    
    for fpath in glob.glob(with_glass):
        light_power = fpath.split("_")[-2]
        with_glass_raw_data = DillSerializer(fpath).deserialize().raw_data
        without_glass_raw_data = DillSerializer(fpath + "out").deserialize().raw_data
        error1 = overall_bit_error_ratio(with_glass_raw_data, groundtruth[light_power])
        error2 = overall_bit_error_ratio(without_glass_raw_data, groundtruth[light_power])
        print("light power: ", light_power)
        print("error with glass: ", error1)
        print("error without glass: ", error2)
        print("diff: ", abs(error1-error2))
        print("---")

if __name__ == "__main__":
    main()
