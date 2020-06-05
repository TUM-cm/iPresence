#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include "shared.h"

#define BUFFER_SIZE 1024
#define MAX_PAYLOAD 1024

struct sockaddr_nl src_addr, dest_addr;
struct nlmsghdr *nlh = NULL;
struct iovec iov;
int sock_fd;
struct msghdr msg;

void setup_netlink(void) {
	sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_USER);
	memset(&src_addr, 0, sizeof(src_addr));
	src_addr.nl_family = AF_NETLINK;
	src_addr.nl_pid = getpid();
	bind(sock_fd, (struct sockaddr *) &src_addr, sizeof(src_addr));

	memset(&dest_addr, 0, sizeof(dest_addr));
	memset(&dest_addr, 0, sizeof(dest_addr));
	dest_addr.nl_family = AF_NETLINK;
	dest_addr.nl_pid = 0; /* For Linux Kernel */
	dest_addr.nl_groups = 0; /* unicast */

	nlh = (struct nlmsghdr *) malloc(NLMSG_SPACE(MAX_PAYLOAD));
	memset(nlh, 0, NLMSG_SPACE(MAX_PAYLOAD));
	nlh->nlmsg_len = NLMSG_SPACE(MAX_PAYLOAD);
	nlh->nlmsg_pid = getpid();
	nlh->nlmsg_flags = 0;

	iov.iov_base = (void *) nlh;
	iov.iov_len = nlh->nlmsg_len;
	msg.msg_name = (void *) &dest_addr;
	msg.msg_namelen = sizeof(dest_addr);
	msg.msg_iov = &iov;
	msg.msg_iovlen = 1;
}

void send_command(char *command) {
	setup_netlink();
	printf("command: %s\n", command);
	strcpy(NLMSG_DATA(nlh), command);
	sendmsg(sock_fd, &msg, 0);
	printf("message sent\n");
}

char *assemble_light_pattern_command(char *action, char *sub_action,
		char *device, char *on_interval, char *off_interval) {
	char *command;
	command = malloc(BUFFER_SIZE);
	strcpy(command, ACTION);
	strcat(command, START_SEPARATOR);
	strcat(command, action);
	strcat(command, STOP_SEPARATOR);
	strcat(command, SUB_ACTION);
	strcat(command, START_SEPARATOR);
	strcat(command, sub_action);
	strcat(command, STOP_SEPARATOR);
	strcat(command, DEVICE);
	strcat(command, START_SEPARATOR);
	strcat(command, device);
	strcat(command, STOP_SEPARATOR);
	strcat(command, ON);
	strcat(command, START_SEPARATOR);
	strcat(command, on_interval);
	strcat(command, STOP_SEPARATOR);
	strcat(command, OFF);
	strcat(command, START_SEPARATOR);
	strcat(command, off_interval);
	strcat(command, STOP_SEPARATOR);
	return command;
}

char *assemble_light_send_command(char *action, char *sub_action, char *device,
		char *time_base_unit, char *msg) {
	char *command;
	command = malloc(BUFFER_SIZE);
	strcpy(command, ACTION);
	strcat(command, START_SEPARATOR);
	strcat(command, action);
	strcat(command, STOP_SEPARATOR);
	strcat(command, SUB_ACTION);
	strcat(command, START_SEPARATOR);
	strcat(command, sub_action);
	strcat(command, STOP_SEPARATOR);
	strcat(command, DEVICE);
	strcat(command, START_SEPARATOR);
	strcat(command, device);
	strcat(command, STOP_SEPARATOR);
	strcat(command, TIME_BASE_UNIT);
	strcat(command, START_SEPARATOR);
	strcat(command, time_base_unit);
	strcat(command, STOP_SEPARATOR);
	strcat(command, MESSAGE);
	strcat(command, START_SEPARATOR);
	strcat(command, msg);
	strcat(command, STOP_SEPARATOR);
	return command;
}

// ./control_led_user pattern start|stop high|low on off
// ./control_led_user send start|stop high|low time_base_unit msg
// time_base_unit = 100000; // 0.1 ms
// time_base_unit = 40000; // 0.05 ms
int main(int argc, char *argv[]) {
	char *action, *sub_action, *device, *on_interval, *off_interval, *msg,
			*time_base_unit, *command;

	if (!(argc == 3 || argc == 4 || argc == 5)) {
		printf("Wrong input data\n");
		exit(-1);
	}
	action = argv[1];
	sub_action = argv[2];
	device = argv[3];
	if (strcmp(action, "send") == 0) {
		// ACTION=send;SUBACTION=start|stop;DEVICE=high|low;TIME_BASE_UNIT=time;MESSAGE=msg;
		if (argc > 4) { // start
			time_base_unit = argv[4];
			msg = argv[5];
		} else { // stop
			msg = "";
			time_base_unit = "0";
		}
		command = assemble_light_send_command(action, sub_action, device,
				time_base_unit, msg);
	} else {
		// ACTION=pattern;SUB_ACTION=start|stop;DEVICE=high|low;ON=on;OFF=off;
		if (argc > 3) { // start
			on_interval = argv[4];
			off_interval = argv[5];
		} else { // stop
			on_interval = "0";
			off_interval = "0";
		}
		command = assemble_light_pattern_command(action, sub_action, device,
				on_interval, off_interval);
	}

	send_command(command);
	return 0;
}

/*
 * Time resolution:
 *
 * 1/2 s     5*10^8
 * 1/10 s    1*10^8
 * 0,01 s    1*10^7
 * 0,005 s   5*10^6
 * 0,001 s   1*10^6
 * 0,0001 s  1*10^5
 */
