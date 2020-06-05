#include <sys/socket.h> // netlink
#include <linux/netlink.h>
#include <string.h> // memset
#include <stdlib.h> // malloc
#include <stdio.h> // printf
#include "shared.h"
#include "user.h"

// gcc configure_light_receiver.c -o configure_light_receiver

struct sockaddr_nl src_addr, dest_addr;
struct nlmsghdr *nlh = NULL;
struct iovec iov;
int sock_fd;
struct msghdr msg;

void setup_netlink(void)
{
	sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_USER);
    memset(&src_addr, 0, sizeof(src_addr));
    src_addr.nl_family = AF_NETLINK;
    src_addr.nl_pid = getpid();
    bind(sock_fd, (struct sockaddr *)&src_addr, sizeof(src_addr));

    memset(&dest_addr, 0, sizeof(dest_addr));
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.nl_family = AF_NETLINK;
    dest_addr.nl_pid = 0; /* For Linux Kernel */
    dest_addr.nl_groups = 0; /* unicast */

    nlh = (struct nlmsghdr *)malloc(NLMSG_SPACE(MAX_PAYLOAD_NETLINK));
    memset(nlh, 0, NLMSG_SPACE(MAX_PAYLOAD_NETLINK));
    nlh->nlmsg_len = NLMSG_SPACE(MAX_PAYLOAD_NETLINK);
    nlh->nlmsg_pid = getpid();
    nlh->nlmsg_flags = 0;

    iov.iov_base = (void *)nlh;
    iov.iov_len = nlh->nlmsg_len;
    msg.msg_name = (void *)&dest_addr;
    msg.msg_namelen = sizeof(dest_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
}

void send_command(char *command)
{
    strcpy(NLMSG_DATA(nlh), command);
    sendmsg(sock_fd, &msg, 0);
}

void calculate_buffer(int interval, int *num_pages, int *page_size)
{
	int values_per_second;
	
	values_per_second = NANOSECOND / interval;
	if (values_per_second <= MAX_PER_SECOND) {
		*page_size = values_per_second;
	} else {
		*page_size = MAX_PER_SECOND;
	}
	*num_pages = MAX_BUFFER_SIZE / *page_size;
}

char *assemble_command(char *action, char *device, char *interval, int num_pages, int page_size)
{
	char *command;
	char buffer[BUFFER_LENGTH];
	
	command = malloc(BUFFER_LENGTH);
	strcpy(command, ACTION);
	strcat(command, START_SEPARATOR);
	strcat(command, action);
	strcat(command, STOP_SEPARATOR);
	strcat(command, DEVICE);
	strcat(command, START_SEPARATOR);
	strcat(command, device);
	strcat(command, STOP_SEPARATOR);
	strcat(command, SENSING_INTERVAL);
	strcat(command, START_SEPARATOR);
	strcat(command, interval);
	strcat(command, STOP_SEPARATOR);
	strcat(command, NUM_PAGES);
	strcat(command, START_SEPARATOR);
	sprintf(buffer, "%d", num_pages);
	strcat(command, buffer);
	strcat(command, STOP_SEPARATOR);
	strcat(command, PAGE_SIZE_T);
	strcat(command, START_SEPARATOR);
	memset(&buffer[0], 0, sizeof(buffer));	
	sprintf(buffer, "%d", page_size);
	strcat(command, buffer);
	strcat(command, STOP_SEPARATOR);
	return command;
}

// args: start|stop pd|led sampling_frequency
int main(int argc, char *argv[])
{
	char *action, *device, *interval, *command;
	int num_pages, page_size;

	if (argc == 2) { // stop
		command = "ACTION=stop;";
	} else if (argc == 4) { // start
		action = argv[1];
		device = argv[2];
		interval = argv[3];
	} else {
		printf("Wrong input data\n");
		exit(-1);
	}
	if (strcmp(action, "start") == 0) {
		calculate_buffer(atoi(interval), &num_pages, &page_size);
		printf("page_size=%d\n", page_size);
		printf("num_pages=%d\n", num_pages);
		command = assemble_command(action, device, interval, num_pages, page_size);
	}
	printf("setup netlink\n");
	setup_netlink();
	printf("send command\n");
	send_command(command);

	return 0;
}
