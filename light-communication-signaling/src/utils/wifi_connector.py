import re
import signal
import pexpect
import logging
import netifaces
import subprocess

def activate_hotspot():
    logging.info("execute hostapd ...")
    subprocess.call("hostapd hotspot.conf &", shell=True)

def activate_networking():
    logging.info("restart networking ...")
    subprocess.call("/etc/init.d/networking restart", shell=True)

def activate_dhcp():
    logging.info("restart dhcp server ...")
    subprocess.call("/etc/init.d/dnsmasq restart", shell=True)
    
def interface_available(interface="wlan0"):
    return (interface in netifaces.interfaces())

def get_ip(interface):
    return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']

# http://variwiki.com/index.php?title=Wifi_connman
# ifconfig wlan0 up
# iwlist wlan0 scan
def connect(ssid, pw):
    stdout = pexpect.run("connmanctl services")
    services = stdout.decode('utf-8').strip().split("\n")
    service_identifier = None
    for service in services:
        if ssid in service:
            service_identifier = re.split("[ ]+", service)[-1]
            print(service_identifier)
            break
    if service_identifier:
        connmanctl = pexpect.spawn("connmanctl")
        connmanctl.sendline("agent on")
        connmanctl.sendline("connect " + service_identifier)
        connmanctl.expect("Passphrase?")
        connmanctl.sendline(pw)
        connmanctl.sendline("quit")
        connmanctl.kill(signal.SIGTERM)
        return True
    else:
        return False
    
def is_connected(ssid, interface="wlan0"):
    out = pexpect.run("iwconfig " + interface)
    pattern = '.* ESSID:"(.*)" .*'
    result = re.findall(pattern, out)
    if result and ssid in result[0]:
        return True
    else:
        out = pexpect.run("iwgetid -r")
        return (ssid in out)

def main():
    print(is_connected("relay"))

if __name__ == "__main__":
    main()
