#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#define SIG_TEST 44 /* we define our own signal, hard coded since SIGRTMIN is different in user and in kernel space */ 

void receiveData(int n, siginfo_t *info, void *unused) {
	printf("received value %i\n", info->si_int);
}

int main(int argc, char **argv) {
	int pid;
	int configfd;
	char buf[10];
	// setup the signal handler for SIG_TEST
	struct sigaction sig;
	sig.sa_sigaction = receiveData;
	sig.sa_flags = SA_SIGINFO;
	sigaction(SIG_TEST, &sig, NULL);

	// kernel needs to know our pid to be able to send us a signal ->
	// we use debugfs for this -> do not forget to mount the debugfs!
	configfd = open("/sys/kernel/debug/signalconfpid", O_WRONLY);
	if (configfd < 0) {
		perror("open");
		return -1;
	}

	pid = getpid();
	sprintf(buf, "%i", pid);
	printf("user pid = %d\n", pid);
	if (write(configfd, buf, strlen(buf) + 1) < 0) {
		perror("fwrite");
		return -1;
	}
	return 0;
}
