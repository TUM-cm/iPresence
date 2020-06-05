#include <sys/socket.h> // netlink
#include <linux/netlink.h>
#include <sys/mman.h> // mmap
#include <fcntl.h> // open
#include <stdlib.h> // malloc
#include <stdio.h> // printf
#include <string.h> // mem functions
#include <unistd.h> // getpid
#include <math.h>
#include <stdbool.h>
#include "callback.h"
#include "shared.h"
#include "user.h"

// mmap data
struct data *data;
int voltage_size;
int time_size;
int prev_idx;
int page_size;
int num_pages;

// netlink control
struct sockaddr_nl src_addr, dest_addr;
struct nlmsghdr *nlh;
struct iovec iov;
int sock_fd;
struct msghdr msg;

// stream control
bool run_stream;

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

    nlh = (struct nlmsghdr *) malloc(NLMSG_SPACE(MAX_PAYLOAD_NETLINK));
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
	printf("nanoseconds: %d\n", NANOSECOND);
	printf("max buffer bytes: %d\n", MAX_BUFFER_BYTES);
	printf("max buffer size: %d\n", MAX_BUFFER_SIZE);
}

char *assemble_start_command(char *action, char *device, char *interval,
		int num_pages, int page_size, int logging)
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

	strcat(command, LOGGING);
	strcat(command, START_SEPARATOR);
	memset(&buffer[0], 0, sizeof(buffer));
	sprintf(buffer, "%d", logging);
	strcat(command, buffer);
	strcat(command, STOP_SEPARATOR);

	return command;
}

int init_mmap(void)
{
	int data_fd;
	size_t length_data;

	voltage_size = page_size * sizeof(int);
	time_size = page_size * sizeof(unsigned int);
	data_fd = open(MMAP_DATA, O_RDONLY);
	if (data_fd < 0) {
		perror("Open data call failed\n");
	}
	length_data = sizeof(struct data);
	printf("create mmap with length: %d\n", length_data);
	data = mmap(0, length_data, PROT_READ, MAP_SHARED, data_fd, 0);
	if (data == MAP_FAILED) {
		perror("data mmap operation failed\n");
	}
	prev_idx = NO_DATA;
	return 1;
}

// Python API

int c_start(char *device, int sampling_interval, int logging)
{
	int len_int_val;
	char *command, *sampling_interval_str;

	calculate_buffer(sampling_interval, &num_pages, &page_size);
	// convert to str
	len_int_val = floor(log10(abs(sampling_interval))) + 1;
	sampling_interval_str = malloc(len_int_val);
	sprintf(sampling_interval_str, "%d", sampling_interval);
	command = assemble_start_command("start", device, sampling_interval_str,
									num_pages, page_size, logging);
	setup_netlink();
	printf("send command: %s\n", command);
	send_command(command);
	init_mmap();
	return 0;
}

int c_stop(void)
{
	char *command;
	command = "ACTION=stop;";
	send_command(command);
	return 0;
}

int c_get_num_pages(void)
{
	return num_pages;
}

int c_get_page_size(void)
{
	return page_size;
}

int c_get_cur_data_idx(void)
{
	return data->latest_page_offset;
}

int c_get_prev_data_idx(void)
{
	return prev_idx;
}

void c_get_data_copy(int* voltage, unsigned int* time)
{
	memcpy(voltage, &data->voltage[c_get_cur_data_idx()], voltage_size);
	memcpy(time, &data->voltage_time[c_get_cur_data_idx()], time_size);
	prev_idx = data->latest_page_offset;
}

void c_get_data_ptr(int* voltage, unsigned int* time)
{
	*voltage = data->voltage[c_get_cur_data_idx()];
	*time = data->voltage_time[c_get_cur_data_idx()];
	prev_idx = data->latest_page_offset;
}

void c_start_stream(streamfunc user_func, void *user_data)
{
	int prev_data_idx;
	run_stream = true;
	prev_data_idx = NO_DATA;
	while(run_stream) {
		if (c_get_cur_data_idx() != prev_data_idx) {
			user_func(&data->voltage[c_get_cur_data_idx()],
					&data->voltage_time[c_get_cur_data_idx()],
					user_data);
			prev_data_idx = c_get_cur_data_idx();
		}
	}
}

int c_stop_stream(void)
{
	run_stream = false;
	return c_stop();
}

int c_calc_page_size(int sampling_interval)
{
	int page_size, num_pages;
	calculate_buffer(sampling_interval, &num_pages, &page_size);
	return page_size;
}

int main(int argc, char *argv[])
{
	return 0;
}
