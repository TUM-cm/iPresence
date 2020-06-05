#ifndef RELEASE_SHARED_H_
#define RELEASE_SHARED_H_

#define NETLINK_USER 17 // 17, 31
#define CONTROL_PATH "control"

#define MMAP_FILE "light_signal"
#define MMAP_PATH "/sys/kernel/debug/"
#define MMAP_DATA MMAP_PATH MMAP_FILE
#define NO_DATA -1

#define START_SEPARATOR "="
#define STOP_SEPARATOR ";"
#define ACTION "ACTION"
#define DEVICE "DEVICE"
#define SENSING_INTERVAL "SENSING_INTERVAL"
#define PAGE_SIZE_T "PAGE_SIZE"
#define NUM_PAGES "NUM_PAGES"
#define LOGGING "LOGGING"

#define MAX_BUFFER_BYTES 8257536
//#define SIZE_SINGLE_BUFFER_ENTRY 8
//#define MAX_BUFFER_SIZE MAX_BUFFER_BYTES/SIZE_SINGLE_BUFFER_ENTRY
#define SIZE_SINGLE_BUFFER_ENTRY 4
#define NUM_BUFFER 2
#define MAX_BUFFER_SIZE MAX_BUFFER_BYTES/(SIZE_SINGLE_BUFFER_ENTRY*NUM_BUFFER)

//#define MAX_BUFFER_SIZE 1032192 // with 8 bytes buffer
//#define MAX_BUFFER_SIZE 516096 // with 12>16 (aligned) bytes buffer
//#define MIN_BUFFER_SIZE 512

struct buffer
{
	int voltage;
	unsigned int time;
};

struct data
{
	int latest_page_offset;
	int voltage[MAX_BUFFER_SIZE];
	unsigned int voltage_time[MAX_BUFFER_SIZE];
	//struct buffer buffer[MAX_BUFFER_SIZE];
};

#endif
