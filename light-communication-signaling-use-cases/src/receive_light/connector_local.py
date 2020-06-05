import numpy
from utils.vlc_interfaces import ReceiverDevice
try:
    import light_receiver
except:
    pass

# make interface, c interface to photodiode
class LocalConnector:
    
    def __init__(self, callback, sampling_interval,
                 receiverDevice=ReceiverDevice.pd, logging=False):
        self.callback = callback
        light_receiver.start(receiverDevice, sampling_interval, logging)
        self.page_size = light_receiver.get_page_size()
        self.run = True
    
    def start(self):
        voltage = numpy.empty(self.page_size, dtype=numpy.int32)
        time = numpy.empty(self.page_size, dtype=numpy.uint32)
        while self.run:
            if (light_receiver.get_cur_data_idx() != light_receiver.get_prev_data_idx()):
                light_receiver.get_data_copy(voltage, time)
                #light_receiver.get_data_ptr(voltage, time)
                self.callback(voltage, time)
                #print("%d, %d" % (voltage.min(), voltage.max()))
                #print("%u, %u" % (time.min(), time.max()))
    
    def stop(self):
        self.run = False
        light_receiver.stop()

    def get_num_pages(self):
        return light_receiver.get_num_pages()
        
    def get_page_size(self):
        return light_receiver.get_page_size()
    
class LocalStreamConnector:
    
    def __init__(self, callback, sampling_interval,
                 receiverDevice=ReceiverDevice.pd, logging=False):
        self.callback = callback
        self.sampling_interval = sampling_interval
        self.receiverDevice = receiverDevice
        self.logging = logging
    
    def start(self):
        light_receiver.start_stream(
            self.receiverDevice, self.sampling_interval, self.callback, self.logging)
    
    def stop(self):
        light_receiver.stop_stream()
    
    def get_num_pages(self):
        return light_receiver.get_num_pages()
        
    def get_page_size(self):
        return light_receiver.get_page_size()
    
def callback(voltage, time):
    print(voltage)
    print(time)
    print("---")

def main():
    localStreamConnector = LocalStreamConnector(callback, 20000)
    localStreamConnector.start()

if __name__ == "__main__":
    main()
