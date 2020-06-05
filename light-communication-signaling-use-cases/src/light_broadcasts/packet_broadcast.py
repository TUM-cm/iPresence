from scapy.all import *

# https://scapy.readthedocs.io/en/latest/build_dissect.html
# https://stackoverflow.com/questions/43711208/scapy-adding-a-new-field-with-a-dynamic-length

class NewField(FieldLenField):
    
    def addfield(self, pkt, s, val):
        return s + "dummy"
    
    def getfield(self, pkt, s):
        return "dummy"

class NewLayer(Packet):
    name = "test"
    fields_desc = [
        NewField("length", None, length_of="data"),
        StrLenField("data", "", length_from=lambda pkt: pkt.length), ]

class UDP(Packet):
    name = "UDP"
    fields_desc = [ ShortEnumField("sport", 53, UDP_SERVICES),
                    ShortEnumField("dport", 53, UDP_SERVICES),
                    ShortField("len", None),
                    XShortField("chksum", None), ]

iface = "Broadcom 802.11ac Network Adapter"
send(UDP(dport=123), iface=iface)
