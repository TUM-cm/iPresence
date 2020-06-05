#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# source: https://www.4armed.com/blog/forging-wifi-beacon-frames-using-scapy/
# 
# requires:
#     radiotap supported wifi nic/driver (frame injection) (works fine with Ralink RT2571W)
#     iwconfig $iface mode monitor
#     iw dev $iface set channel $channel
#       or
#     iwlist iface scan
#  
# example:
#    spawn 1000 essids (0-999)
#    #> python fakebeacon.py $(python -c "print ' '.join(i for i in range(1000))")
#

# https://gist.github.com/tintinweb/04c14d1497001e55e6c10ca28f198fbe

from scapy.all import Dot11,Dot11Beacon,Dot11Elt,RadioTap,sendp,hexdump,RandMAC
import sys
import random
import os

def main():
    ssids = ["idiot"]
    iface = "Broadcom 802.11ac Network Adapter"
    frames = []
    for netSSID in ssids:
        dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff',
        addr2=str(RandMAC()), addr3=str(RandMAC()))
        beacon = Dot11Beacon(cap='ESS+privacy')
        essid = Dot11Elt(ID='SSID',info=netSSID, len=len(netSSID))
        rsn = Dot11Elt(ID='RSNinfo', info=(
          '\x01\x00'                 #RSN Version 1
          '\x00\x0f\xac\x02'         #Group Cipher Suite : 00-0f-ac TKIP
          '\x02\x00'                 #2 Pairwise Cipher Suites (next two lines)
          '\x00\x0f\xac\x04'         #AES Cipher
          '\x00\x0f\xac\x02'         #TKIP Cipher
          '\x01\x00'                 #1 Authentication Key Managment Suite (line below)
          '\x00\x0f\xac\x02'         #Pre-Shared Key
          '\x00\x00'))               #RSN Capabilities (no extra capabilities)

        frame = RadioTap()/dot11/beacon/essid/rsn
        print "SSID=%-20s   %r"%(netSSID,frame)
        frames.append(frame)
    sendp(frames, iface=iface, inter=0.0100 if len(frames)<10 else 0, loop=1)
    
if __name__=="__main__":
    main()
