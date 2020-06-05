#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <asm/siginfo.h>
#include <linux/rcupdate.h>
#include <linux/sched.h>
#include <linux/debugfs.h>
#include <linux/uaccess.h>

#define SIG_TEST 44    // we choose 44 as our signal number (real-time signals are in the range of 33 to 64)

struct dentry *file;

// handover pid of user process via debugfs or ioctl

static ssize_t write_pid(struct file *file, const char __user *buf, size_t count, loff_t *ppos)
{
	char mybuf[10];
	int pid = 0;
	int ret;
	unsigned long missingBytes;
	struct siginfo info;
	struct task_struct *t;

	/* read the value from user space */
	missingBytes = copy_from_user(mybuf, buf, count);
	sscanf(mybuf, "%d", &pid);
	printk("pid = %d\n", pid);
	printk("missing bytes = %lu\n", missingBytes);

	/* send the signal */
	memset(&info, 0, sizeof(struct siginfo));
	info.si_signo = SIG_TEST;
	info.si_code = SI_QUEUE;
	info.si_int = 1234; // real time signals may have 32 bits of data.

	rcu_read_lock();
	t = pid_task(find_get_pid(pid), PIDTYPE_PID);
	if(t == NULL) {
		printk("no such pid\n");
		rcu_read_unlock();
		return -ENODEV;
	}
	rcu_read_unlock();
	ret = send_sig_info(SIG_TEST, &info, t);    //send the signal
	if (ret < 0) {
		printk("error sending signal\n");
		return ret;
	}
	return count;
}

static const struct file_operations my_fops = { .write = write_pid, };

static int __init signalexample_module_init(void)
{
	/* handover pid of user space process via debugfs
	 * As soon as a pid is written to this file,
	 * a signal is sent to that pid */
	file = debugfs_create_file("signalconfpid", 0200, NULL, NULL, &my_fops);
	return 0;
}

static void __exit signalexample_module_exit(void)
{
	debugfs_remove(file);
}

module_init( signalexample_module_init);
module_exit( signalexample_module_exit);
MODULE_LICENSE("GPL");
