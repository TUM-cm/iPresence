echo "insert vlc driver"
insmod vlc.ko frq=50 pool_size=5 mtu=1300 mac_or_app=1 self_id=9 dst_id=8

echo "set ip"
ifconfig vlc0 192.168.0.2

echo "set transmitter: 1 is high-power LED"
echo 1 > /proc/vlc/tx

echo "set receiver: 1 is PD"
echo 1 > /proc/vlc/rx
