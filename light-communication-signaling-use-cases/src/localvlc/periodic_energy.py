import time
import numpy
import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine

class PeriodicEnergyMeasurement:
    
    def __init__(self):
        self.HVMON = HVPM.Monsoon()
        self.HVMON.setup_usb()
        print("HVPM Serial Number: " + repr(self.HVMON.getSerialNumber()))
        self.HVMON.fillStatusPacket()
        self.HVengine = sampleEngine.SampleEngine(self.HVMON)
        self.HVengine.ConsoleOutput(False)
        self.HVengine.disableCSVOutput()
    
    def measure_baseline(self):
        self.HVengine.periodicStartSampling()
        current = list()
        voltage = list()
        for i in range(5):
            print("round: ", i)
            samples = self.HVengine.periodicCollectSamples(100)
            timestamp = samples[sampleEngine.channels.timeStamp]
            mainCurrent = samples[sampleEngine.channels.MainCurrent]
            mainVoltage = samples[sampleEngine.channels.MainVoltage]    
            print("first timestamp: ", timestamp[0])
            print("last timestamp: ", timestamp[-1])
            print("current: ", numpy.mean(mainCurrent))
            print("voltage: ", numpy.mean(mainVoltage))
            current.extend(mainCurrent)
            voltage.extend(mainVoltage)
            time.sleep(5)
        print("overall current: ", numpy.mean(current))
        print("overall voltage: ", numpy.mean(voltage))
        self.HVengine.periodicStopSampling()
        self.HVMON.closeDevice()
    
def main():
    measurement = PeriodicEnergyMeasurement()
    measurement.measure_baseline()
    
if __name__ == "__main__":
    main()
