#include <sys/socket.h> // netlink
#include <linux/netlink.h>
#include <sys/mman.h> // mmap
#include <fcntl.h> // open
#include <string.h> // memset
#include <unistd.h> // close
#include <stdlib.h> // malloc
#include <stdio.h> // FILE
#include <stdint.h> // uint64_t or #include <inttypes.h>
#include "shared.h"
#include "user.h"
#include "MQTTClient.h"

// gcc user_release.c -lpaho-mqtt3c -o user_release

// netlink
struct sockaddr_nl src_addr, dest_addr;
struct nlmsghdr *nlh = NULL;
struct iovec iov;
int sock_fd;
struct msghdr msg;

// data
int control_fd;
char *control = NULL; // 1=49, 0=48
int data_fd;
struct data *data = NULL;
size_t length_control;
size_t length_data;

// mqtt
MQTTClient client;
MQTTClient_message pubmsg = MQTTClient_message_initializer;
MQTTClient_deliveryToken token;

int inline fast_atoi(const char *str)
{
    int val = 0;
    while(*str) {
        val = val*10 + (*str++ - '0');
    }
    return val;
}

char *get_mac()
{
    char *mac = malloc(BUFFER_LENGTH);
    FILE *fptr;
    if ((fptr = fopen(PATH_MAC, "r")) == NULL) {
        printf("Error! opening file");
        exit(1);
    }
    fscanf(fptr, "%s", mac);
    fclose(fptr);
    return mac;
}

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

void setup_mqtt(int page_size)
{
	char *client_id;
	MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;

    conn_opts.keepAliveInterval = KEEP_ALIVE;
    pubmsg.qos = QOS;
	//pubmsg.payloadlen = PAGE_ELEMENTS * sizeof(struct buffer);
	pubmsg.payloadlen = page_size * sizeof(struct buffer);
	//pubmsg.payloadlen = page_size * sizeof(int);
    client_id = get_mac();
    //client_id = "192.168.7.2";
    printf("client id: %s\n", client_id);
    MQTTClient_create(&client, ADDRESS, client_id, MQTTCLIENT_PERSISTENCE_NONE, NULL);
    if (MQTTClient_connect(client, &conn_opts) != MQTTCLIENT_SUCCESS) {
    	perror("MQTT failed to connect.\n");
    }
}

void setup_mainloop(int num_pages, int page_size)
{
	length_control = 1;
	printf("control data\n");
	control_fd = open(CONTROL_PATH, O_RDONLY);
	if (control_fd < 0) {
		perror("Open data call failed\n");
	}
	control = mmap(0, length_control, PROT_READ, MAP_SHARED, control_fd, 0);
	if (control == MAP_FAILED) {
		perror("control mmap operation failed\n");
	}
	printf("control: %d\n", fast_atoi(control));

	printf("data\n");
	printf("open: %s\n", MMAP_DATA);
	data_fd = open(MMAP_DATA, O_RDONLY);
	if (data_fd < 0) {
		perror("Open data call failed\n");
	}
	//length_data = sizeof(int) + BUFFER_SIZE * sizeof(struct buffer);
	length_data = sizeof(int) + (num_pages * page_size) * sizeof(struct buffer);
	//length_data = sizeof(int) + (num_pages * page_size) * sizeof(int);
	data = mmap(0, length_data, PROT_READ, MAP_SHARED, data_fd, 0);
	if (data == MAP_FAILED) {
		perror("data mmap operation failed\n");
	}
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

// ./read_light_user pd|led sampling_frequency
int main(int argc, char *argv[])
{
	int page, page_offset, num_pages, page_size, buffer_size, i, prev;
	struct buffer *buffer;
	//int *buffer;
	char *device, *interval, *start_command, *stop_command;

	if (argc != 3) {
		printf("Wrong input data\n");
		exit(-1);
	}

	device = argv[1];
	interval = argv[2];
	printf("device: %s, interval: %s\n", device, interval);
	
	printf("calculate buffer\n");
	calculate_buffer(atoi(interval), &num_pages, &page_size);
	buffer_size = page_size * sizeof(struct buffer);
	//buffer_size = page_size * sizeof(int);
	buffer = malloc(buffer_size);
	printf("max buffer size: %d\n", MAX_BUFFER_SIZE);
	printf("size of buffer: %d\n", sizeof(struct buffer));
	printf("num pages: %d, page size: %d\n", num_pages, page_size);
	
	// ACTION=start|stop;DEVICE=pd|led;SENSING_INTERVAL=20000;
	start_command = assemble_command("start", device, interval, num_pages, page_size);
	stop_command = "ACTION=stop;";
	
	printf("start command: %s\n", start_command);
	printf("stop command: %s\n", stop_command);
	
	printf("setup netlink\n");
	setup_netlink();
	printf("setup mqtt\n");
	setup_mqtt(page_size);
	
	printf("setup mainloop\n");
	setup_mainloop(num_pages, page_size);
	
	printf("send start command\n");	
	send_command(start_command);
	
	page = 0;
	page_offset = 0;
	prev = -1;
	while(fast_atoi(control)) {
		if (data->latest_page_offset != prev) {
			memcpy(buffer, &data->buffer[page_offset], buffer_size);
	    	pubmsg.payload = buffer;
	        MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token);
			page_offset += page_size;
	        page++;
	        prev = data->latest_page_offset;
			if (page == num_pages) {
				page = 0;
				page_offset = 0;
			}
		}
	}
	
	printf("stop command\n");
	// ACTION=start|stop;DEVICE=pd|led;
	send_command(stop_command);
	
	munmap(control, length_control);
	close(control_fd);
	munmap(data, length_data);
	close(data_fd);
	
	return 0;
}
