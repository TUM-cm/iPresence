#include <sys/mman.h> // mmap
#include <fcntl.h>    // open
#include <stdlib.h>   // malloc
#include <stdio.h>    // printf
#include <string.h>   // memcpy
#include "shared.h"

struct data *data;
struct buffer *buffer;
int buffer_size;

// args: num_pages page_size
int main(int argc, char *argv[])
{
	int i, page, page_offset, prev, buffer_size, data_fd, num_pages, page_size;
	size_t length_data;
	struct buffer *buffer;
	struct data *data = NULL;

	if (argc != 3) {
		printf("Wrong input data\n");
		exit(-1);
	}
	num_pages = atoi(argv[1]);
	page_size = atoi(argv[2]);
	buffer_size = page_size * sizeof(struct buffer);
	buffer = malloc(buffer_size);

	data_fd = open(MMAP_DATA, O_RDONLY);
	if (data_fd < 0) {
		perror("Open data call failed\n");
	}
	length_data = sizeof(int) + (num_pages * page_size) * sizeof(struct buffer);
	data = mmap(0, length_data, PROT_READ, MAP_SHARED, data_fd, 0);
	if (data == MAP_FAILED) {
		perror("data mmap operation failed\n");
	}
	page = 0;
	page_offset = 0;
	prev = -1;
	while(1) {
		if (data->latest_page_offset != prev) {
			memcpy(buffer, &data->buffer[page_offset], buffer_size);
			printf("page index: %d\n", data->latest_page_offset);
			for(i = 0; i < 10; i++) {
				printf("%d ", buffer[i]);
			}
			printf("\n");
	        page_offset += page_size;
	        page++;
	        prev = data->latest_page_offset;
			if (page == num_pages) {
				page = 0;
				page_offset = 0;
			}
		}
	}

	return 0;
}
