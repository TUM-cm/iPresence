# import netifaces
# 
# ifaces = netifaces.interfaces()
# for iface in ifaces:
#     addrs = netifaces.ifaddresses(iface)
#     print "name: ", iface
#     print addrs
#     # netifaces.AF_INET | netifaces.AF_LINK
#     print addrs[netifaces.AF_LINK]
#     print "---"

'''
1) Turn the interface down via “ifconfig wlp0s29u1u7 down”
2) Set the device to monitor mode via “iwconfig wlp0s29u1u7 mode monitor”
3) Turn the interface back on via “ifconfig wlp0s29u1u7 up”
4) Set the interface to a certain channel via “iwconfig wlp0s29u1u7 chan 6”
5) If the settings were correctly adapted, the output of “iwconfig wlp0s29u1u7” includes “Mode:Monitor” and “Frequency:2.437 GHz” (for channel 6 in this example).

'''

import time
import struct
import threading

from scapy.all import *

# https://github.com/rpp0/scapy-fakeap/blob/master/fakeap/callbacks.py
  
#iface = "Broadcom NetXtreme Gigabit Ethernet" # connected via cable
iface = "Broadcom 802.11ac Network Adapter" # connected via 
sc = 0
channel = 1
boottime = time.time()
ssid = "idiot"
mac = "ac:bc:32:cc:ae:5b"
interval = 0.1

AP_RATES = "\x0c\x12\x18\x24\x30\x48\x60\x6c"

def next_sc():
    global sc
    sc = (sc + 1) % 4096
    return sc * 16  # Fragment number -> right 4 bits
 
def current_timestamp():
    return (time.time() - boottime) * 1000000

def get_frequency(channel):
    if channel == 14:
        freq = 2484
    else:
        freq = 2407 + (channel * 5)
    freq_string = struct.pack("<h", freq)
    return freq_string

def get_radiotap_header():
    return RadioTap(len=18, present='Flags+Rate+Channel+dBm_AntSignal+Antenna', notdecoded='\x00\x6c' + get_frequency(channel) + '\xc0\x00\xc0\x01\x00\x00')

def dot11_beacon(ssid):
    beacon_packet = get_radiotap_header()                                           \
                / Dot11(subtype=8, addr1='ff:ff:ff:ff:ff:ff', addr2=mac, addr3=mac) \
                / Dot11Beacon(cap=0x2105)                                           \
                / Dot11Elt(ID='SSID', info=ssid)                                    \
                / Dot11Elt(ID='Rates', info=AP_RATES)                               \
                / Dot11Elt(ID='DSset', info=chr(channel))
    
    # Update sequence number
    beacon_packet.SC = next_sc()
    
    # Update timestamp
    beacon_packet[Dot11Beacon].timestamp = current_timestamp()
    #beacon_packet.show()
    
    #print beacon_packet.SC
    #print beacon_packet[Dot11Beacon].timestamp
    
    sendp(beacon_packet, iface=iface, verbose=False)

class FakeBeaconTransmitter(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while True:
            dot11_beacon(ssid)
            time.sleep(interval)

#sendp(packet, iface=iface, count=1000) # amount
#sendp(packet, iface=iface, loop=1) # endless loop

#beacon_transmitter = FakeBeaconTransmitter()
#beacon_transmitter.start()

while True:
    dot11_beacon(ssid)
    time.sleep(interval)
