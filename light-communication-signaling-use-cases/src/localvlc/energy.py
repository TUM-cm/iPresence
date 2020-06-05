import time
import numpy
import datetime
import itertools
import threading
import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine

# A * V = W
# A = W / V
# Wh / V = Ah
# W = J / s > J = W * s

def setup_voltage():
    HVMON = HVPM.Monsoon()
    HVMON.setup_usb()
    print("HVPM Serial Number: " + repr(HVMON.getSerialNumber()))
    HVMON.fillStatusPacket()
    HVMON.setVout(5)
    HVMON.closeDevice()

def format_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

class EnergyMeasurements:
    
    def __init__(self, collect_duration=600, collect_samples=100, collect_repeat_period=0.5):
        self.HVMON, self.HVengine = self.__create_engine()
        self.collect_duration = collect_duration
        self.collect_samples = collect_samples
        self.collect_repeat_period = collect_repeat_period
        self.samples = list()
        self.timer = None
    
    def measure_baseline_periodic(self, rounds=20, sleep=10):
        self.HVengine.periodicStartSampling()
        current = list()
        voltage = list()
        timestamp = list()
        for i in range(rounds):
            print("round: ", i)
            samples = self.HVengine.periodicCollectSamples(self.collect_samples)
            mainTimestamp = samples[sampleEngine.channels.timeStamp]
            mainCurrent = samples[sampleEngine.channels.MainCurrent]
            mainVoltage = samples[sampleEngine.channels.MainVoltage]    
            timestamp.extend(mainTimestamp)
            current.extend(mainCurrent)
            voltage.extend(mainVoltage)
            print("num. samples: ", len(mainCurrent))
            print("first timestamp: ", mainTimestamp[0])
            print("last timestamp: ", mainTimestamp[-1])
            print("mean current (mA): ", numpy.mean(mainCurrent))
            print("mean voltage (V): ", numpy.mean(mainVoltage))
            print("sleep")
            time.sleep(sleep)
        self.HVengine.periodicStopSampling()
        self.closeDevice()
        scaledMainCurrent = [x / 1000 for x in current]
        mainPower = numpy.multiply(scaledMainCurrent, voltage) # U * I = V * A
        duration = timestamp[-1]
        num_samples = len(current)
        current = numpy.mean(current)
        voltage = numpy.mean(voltage)
        energy_Wh = (numpy.mean(mainPower) * duration) / 3600 # U * I * t, V * A * s(=h)
        print("num. samples: ", num_samples)
        print("duration (s): ", duration)
        print("mean current (mA): ", current)
        print("mean voltage (V): ", voltage)
        print("power (W): ", numpy.mean(mainPower))
        print("power (Wh): ", energy_Wh)
        print("energy (J): ", energy_Wh * 3600)
    
    def measure_baseline(self, duration=None):
        numSamples = sampleEngine.triggers.SAMPLECOUNT_INFINITE 
        self.HVengine.setStartTrigger(sampleEngine.triggers.GREATER_THAN, 0)
        if duration:
            self.collect_duration = duration
        self.HVengine.setStopTrigger(sampleEngine.triggers.GREATER_THAN, self.collect_duration) 
        self.HVengine.setTriggerChannel(sampleEngine.channels.timeStamp)
        self.HVengine.startSampling(numSamples)
        samples = self.HVengine.getSamples()
        self.closeDevice()
        current = samples[sampleEngine.channels.MainCurrent]
        timestamp = samples[sampleEngine.channels.timeStamp]
        print("duration: ", timestamp[-1])
        print("Num. samples: ", len(current))
        return numpy.mean(current)
    
    def start_periodic_sampling(self):
        
        def run():
            print("collect energy samples")
            samples = self.HVengine.periodicCollectSamples(self.collect_samples)
            self.samples.append(samples)
            self.timer = threading.Timer(self.collect_repeat_period, run)
            self.timer.start()
        
        print("before start sampling")
        self.HVengine.periodicStartSampling()
        print("after start sampling")
        run()
    
    def stop_periodic_sampling(self):
        try:
            self.timer.cancel()
        except:
            pass
        self.HVengine.periodicStopSampling()
    
    def closeDevice(self):
        self.HVMON.closeDevice()
    
    def reset(self):
        self.samples = list()
    
    def __create_engine(self):
        HVMON = HVPM.Monsoon()
        HVMON.setup_usb()
        print("HVPM Serial Number: " + repr(HVMON.getSerialNumber()))
        HVMON.fillStatusPacket()
        #HVMON.setVout(5)
        HVengine = sampleEngine.SampleEngine(HVMON)
        HVengine.ConsoleOutput(False)
        HVengine.disableCSVOutput()
        #HVengine.enableChannel(sampleEngine.channels.MainCurrent)
        #HVengine.enableChannel(sampleEngine.channels.MainVoltage)
        #HVengine.enableChannel(sampleEngine.channels.timeStamp)
        return HVMON, HVengine
    
    def __get_results(self):
        current = list(itertools.chain.from_iterable([sample[sampleEngine.channels.MainCurrent] for sample in self.samples]))
        voltage = list(itertools.chain.from_iterable([sample[sampleEngine.channels.MainVoltage] for sample in self.samples]))
        #timestamp = list(itertools.chain.from_iterable([sample[sampleEngine.channels.timeStamp] for sample in self.samples]))
        print("Num. current: ", len(current))
        print("Num. voltage: ", len(voltage))
        #print("Num. timestamp: ", len(timestamp))
        return current, voltage
    
    def calculate_energy(self, duration):
        current, voltage = self.__get_results()
        current = numpy.mean(current) # mA
        voltage = numpy.mean(voltage) # V
        print("duration: ", duration)
        print("voltage: ", voltage)
        print("current: ", current)
        # P = U * I
        # E = P * t = U * I * t # Wh
        # E = I * t # uAh
        power_mW = voltage * current # mA * V
        #energy_uAh = ((current * duration) / 3600) * 1000
        energy_mWh = (power_mW * duration) / 3600
        energy_mJ = energy_mWh * 3600 # 1 Wh = 3600 Joule
        print("energy (mWh): ", energy_mWh)
        print("energy (mJ): ", energy_mJ)
        return energy_mJ
    
def sample_test():
    energyMeasurements = EnergyMeasurements()
    for i in range(5):
        print("round: ", i)
        energyMeasurements.start_periodic_sampling()
        start = time.time()
        time.sleep(2) # do performance evaluation
        duration = time.time() - start
        energyMeasurements.stop_periodic_sampling()
        energyMeasurements.calculate_energy(duration)
        energyMeasurements.reset()
    energyMeasurements.closeDevice()
    
def main():
    #setup_voltage()
    sample_test()
    
if __name__ == "__main__":
    main()
