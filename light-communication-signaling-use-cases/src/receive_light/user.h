#ifndef RELEASE_USER_H_
#define RELEASE_USER_H_

#define ADDRESS "tcp://localhost:1883"
#define TOPIC "beaglebone"
#define QOS 0
#define KEEP_ALIVE 20
#define PATH_MAC_ETH "/sys/class/net/eth0/address"
#define PATH_MAC_USB "/sys/class/net/usb0/address"
#define PATH_MAC PATH_MAC_ETH

#define NANOSECOND 1000000000
#define MAX_PER_SECOND 10000

#define MAX_PAYLOAD_NETLINK 1024
#define BUFFER_LENGTH 200

#endif
