try:
    import utils.kernel_module
    utils.kernel_module.add_light_sender()
except:
    pass
import os
import logging
import collections
import subprocess
from utils.custom_enum import enum_name
from utils.vlc_interfaces import SenderAction
from utils.vlc_interfaces import SenderDevice

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

parameter = enum_name("action", "device",
                      "time_base_unit", "revert_phases",
                      "pattern_on", "pattern_off",
                      "data", "data_file", "pattern",
                      "coupling_feedback_duration")

class LightSender:
    
    def __init__(self, control_program="send_light_kernel.ko", **kwargs):
        self.control_program = control_program
        self.full_path_control_program = os.path.join(__location__, control_program)
        self.args = collections.OrderedDict([
            (parameter.action, SenderAction.send),
            (parameter.device, SenderDevice.high),
            (parameter.time_base_unit, 100000),
            (parameter.revert_phases, None),
            (parameter.pattern_on, None),
            (parameter.pattern_off, None),
            (parameter.data, None),
            (parameter.data_file, None),
            (parameter.pattern, None),
            (parameter.coupling_feedback_duration, None)])
        for key, value in kwargs.items():
            self.__set_value(key, value)
    
    def __set_value(self, key, value):
        if key in self.args.keys():
            self.args[key] = value
    
    def set_device(self, device):
        self.__set_value(parameter.device, device)
    
    def set_time_base_unit(self, time_base_unit):
        self.__set_value(parameter.time_base_unit, time_base_unit)
    
    def set_coupling_feedback(self, action, duration=None):
        self.__set_value(parameter.action, "'\"" + action + "\"'")
        if duration:
            self.__set_value(parameter.coupling_feedback_duration, duration)
    
    def set_pattern(self, pattern_on, pattern_off):
        self.__set_value(parameter.action, SenderAction.pattern)
        self.__set_value(parameter.pattern_on, pattern_on)
        self.__set_value(parameter.pattern_off, pattern_off)
    
    def set_data(self, data):
        self.__set_value(parameter.action, SenderAction.send)
        self.__set_value(parameter.data,  "'\"" + data + "\"'")
    
    def set_data_file(self, f):
        self.__set_value(parameter.action, SenderAction.send)
        self.__set_value(parameter.data_file, f)
    
    def set_pattern_series(self, pattern):
        self.__set_value(parameter.time_base_unit, None)
        self.__set_value(parameter.action, SenderAction.pattern)
        pattern = ",".join(map(str, pattern))
        self.__set_value(parameter.pattern, pattern)
    
    def set_revert_phases(self, revert_phases):
        self.__set_value(parameter.revert_phases, revert_phases)
    
    def write_data(self, data):
        with open(self.args[parameter.data_file], 'w') as f:
            f.write(data)
    
    def start(self):
        logging.info("start light sender ...")
        cmd = self.get_start()
        logging.debug(cmd)
        print(cmd)
        return self.execute(cmd)
    
    def stop(self):
        logging.info("stop light sender")
        cmd = self.get_stop()
        logging.debug(cmd)
        print(cmd)
        return self.execute(cmd)
    
    def check_active(self):
        search_value = self.get_program_name(self.control_program)
        out = subprocess.check_output("lsmod")
        return (search_value in out)
    
    def execute(self, command):
        logging.info(command)
        return subprocess.call(command, shell=True)
    
    def get_program_name(self, program):
        return program.split(".")[0]
    
    def get_start(self):
        command = "insmod " + self.full_path_control_program
        for key, value in self.args.items():
            if value != None:
                command += (" " + key + "=" + str(value))
        return command
    
    def get_stop(self):
        return "rmmod " + self.get_program_name(self.control_program)
    
def main():
    light_sender = LightSender("send_light_kernel.ko")
    light_sender.set_data("hello world")
    print(light_sender.get_start())
    print(light_sender.get_stop())
    light_sender.start()
    print(light_sender.check_active())
    light_sender.stop()
    
if __name__ == "__main__":
    main()
