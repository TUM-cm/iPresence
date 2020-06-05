#include <fcntl.h>  
#include <unistd.h>  
#include <sys/mman.h>  
#include <stdio.h>
#include <string.h>
#include<errno.h>

#define DEVICE_FILENAME "/dev/mchar"  

int main() {
	int fd;
	int ret;
	char *p = NULL;
	char buff[64];

	fd = open(DEVICE_FILENAME, O_RDWR | O_NDELAY);
	if (fd >= 0) {
		p = (char*) mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
		printf("%s\n", p);
		munmap(p, 4096);

		close(fd);
	}

	fd = open(DEVICE_FILENAME, O_RDWR | O_NDELAY);
	ret = write(fd, "abcd", strlen("abcd"));
	if (ret < 0) {
		printf("write error!\n");
		return errno;
	}

	ret = read(fd, buff, 64);
	if (ret < 0) {
		printf("read error!\n");
		return errno;
	}
	printf("read: %s\n", buff);

	return 0;
}
