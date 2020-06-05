#include <net/sock.h>
#include <rtdm/rtdm_driver.h>
#include <linux/gpio.h>
#include <linux/debugfs.h>
#include "shared.h"
#include "kernel.h"

// light signal
int bit_clc = 1 << BIT_CLC;
int bit_cs = 1 << BIT_CS;
volatile void* gpio1;
volatile void* gpio2;
int rx;

rtdm_timer_t timer; // timer
struct sock *sock; // netlink

// mmap
struct dentry *mmap_file;
struct data *data;

int page;
int page_idx;
int page_offset;
unsigned int clock; // 4.294.967.295
uint32_t clock_interval;

int i;
int pos;
int num_pages;
int page_size;
bool logging;

char *get_value(char *command, char *search_token) {
	char *tmp_command, *part, *token;
	size_t command_size, token_size;

	command_size = strlen(command);
	token_size = strlen(search_token);
	tmp_command = kmalloc(command_size, GFP_KERNEL);
	strncpy(tmp_command, command, command_size);
	while ((part = strsep(&tmp_command, STOP_SEPARATOR)) != NULL) {
		token = strsep(&part, START_SEPARATOR);
		if (strncmp(token, search_token, token_size) == 0) {
			return strsep(&part, START_SEPARATOR);
		}
	}
	return NULL;
}

// Delay in terms of count
void inline delay_n_NOP(void) {
	for (i = SPI_DELAY_CNT; i > 0; i--)
		;
}

// Write SFD and channel ID to the ADC
void SPI_write_sfd_and_ch(void) {
	unsigned char write_byte = 0x18 + rx; // 0001 1000 channel 0 of the AD
	unsigned char shift = 0x10; // 0001 1000
	while (shift > 0) {
		writel(bit_clc, gpio2 + CLEAR_OFFSET);
		delay_n_NOP();
		if ((_Bool) (write_byte & shift)) {
			writel(1 << BIT_MOSI, gpio2 + SET_OFFSET);
			delay_n_NOP();
		} else {
			writel(1 << BIT_MOSI, gpio2 + CLEAR_OFFSET);
			delay_n_NOP();
		}
		shift >>= 1;
		writel(bit_clc, gpio2 + SET_OFFSET);
	}
}

int SPI_read_from_adc(void) {
	unsigned int value = 0, index;
	writel(bit_cs, gpio1 + CLEAR_OFFSET);
	delay_n_NOP();
	SPI_write_sfd_and_ch();
	// Skip the first interval
	writel(bit_clc, gpio2 + CLEAR_OFFSET);
	delay_n_NOP();
	writel(bit_clc, gpio2 + SET_OFFSET);
	delay_n_NOP();
	// Read the value
	for (index = 0; index < 11; index++) {
		writel(bit_clc, gpio2 + CLEAR_OFFSET);
		delay_n_NOP();
		value <<= 1;
		value |= (0x1 & (readl(gpio1 + READ_OFFSET) >> BIT_MISO));
		writel(bit_clc, gpio2 + SET_OFFSET);
		delay_n_NOP();
	}
	writel(bit_clc, gpio2 + CLEAR_OFFSET);
	delay_n_NOP();
	writel(bit_cs, gpio1 + SET_OFFSET);
	delay_n_NOP();
	return value;
}

void sensing_handler(rtdm_timer_t *timer) {
	//rtdm_printk("%d\n", SPI_read_from_adc());
	pos = page_idx + page_offset;
	data->voltage[pos] = SPI_read_from_adc();
	data->voltage_time[pos] = clock;
	clock += clock_interval;
	page_idx++;
	if (page_idx == page_size) {
		if (logging) {
			// typedef uint64_t nanosecs_abs_t, rtdm_clock_read()
			rtdm_printk("data size: %d, time monotonic: %llu\n",
					page_size, rtdm_clock_read_monotonic());
			/*rtdm_printk("voltage size: %d, voltage time size: %d\n",
					sizeof(data->voltage[pos]), sizeof(data->voltage_time[pos]));*/
		}
		data->latest_page_offset = page_offset;
		page_idx = 0;
		page_offset += page_size;
		page++;
		// reset to avoid clock jumps over time, leading to wrong duration
		// drawback: receive slow information over one frame is not possible
		clock = 0;
		if (page == num_pages) {
			page = 0;
			page_offset = 0;
		}
	}
}

void handle_command(char *action, char *device, uint32_t sensing_interval) {
	rtdm_timer_destroy(&timer);
	if (strcmp(action, "start") == 0) {
		page = 0;
		clock = 0;
		page_idx = 0;
		page_offset = 0;
		data->latest_page_offset = NO_DATA;
		clock_interval = sensing_interval / CONVERT_SENSING_INTERVAL;
		if (strcmp(device, "pd") == 0) { // photodiode as RX
			rtdm_printk("photodiode as receiver\n");
			rx = 1;
			gpio_direction_output(GPIO_LED_OR_PD, GPIOF_INIT_LOW);
		} else { // low power LED as RX
			rtdm_printk("led as receiver\n");
			rx = 0;
			gpio_direction_output(GPIO_LED_OR_PD, GPIOF_INIT_HIGH);
		}
		rtdm_printk("--- start sensing\n");
		rtdm_timer_init(&timer, sensing_handler, "sensing");
		rtdm_timer_start(&timer, 0, sensing_interval, RTDM_TIMERMODE_RELATIVE);
	} else if (strcmp(action, "stop") == 0) {
		rtdm_printk("--- stop sensing\n");
	}
}

void nl_recv_msg(struct sk_buff *skb) {
	struct nlmsghdr *nlh;
	uint32_t sensing_interval;
	char *command, *action, *device;
	int ret, logging_value;

	nlh = (struct nlmsghdr *) skb->data;
	command = (char *) nlmsg_data(nlh);
	action = get_value(command, ACTION);
	if (strcmp(action, "start") == 0) {
		device = get_value(command, DEVICE);
		ret = kstrtouint(get_value(command, SENSING_INTERVAL), 10,
				&sensing_interval);
		ret = kstrtouint(get_value(command, NUM_PAGES), 10, &num_pages);
		ret = kstrtouint(get_value(command, PAGE_SIZE_T), 10, &page_size);
		ret = kstrtouint(get_value(command, LOGGING), 10, &logging_value);
		logging = (logging_value == 0 ? false : true);
		rtdm_printk("num pages: %d\n", num_pages);
		rtdm_printk("page size: %d\n", page_size);
		rtdm_printk("logging: %d\n", logging);
	} else { // stop
		device = NULL;
		sensing_interval = 0;
	}
	rtdm_printk("action: %s\n", action);
	rtdm_printk("device: %s\n", device);
	rtdm_printk("sensing interval: %d\n", sensing_interval);
	handle_command(action, device, sensing_interval);
}

int op_mmap(struct file *filp, struct vm_area_struct *vma) {
	vma->vm_private_data = filp->private_data;
	// remap kernel memory to userspace
	remap_pfn_range(vma, vma->vm_start, virt_to_phys(data) >> PAGE_SHIFT,
			vma->vm_end - vma->vm_start, vma->vm_page_prot);
	return 0;
}

int mmapfop_close(struct inode *inode, struct file *filp) {
	filp->private_data = NULL;
	return 0;
}

int mmapfop_open(struct inode *inode, struct file *filp) {
	filp->private_data = data;
	return 0;
}

static const struct file_operations mmap_fops = { .open = mmapfop_open,
		.release = mmapfop_close, .mmap = op_mmap, };

int init_module(void) {
	struct netlink_kernel_cfg cfg;

	cfg.input = nl_recv_msg;
	sock = netlink_kernel_create(&init_net, NETLINK_USER, &cfg);
	if (!sock) {
		rtdm_printk(KERN_ALERT "Error creating socket.\n");
		return -ENOMEM;
	}

	if (gpio_request(GPIO_LED_OR_PD, "LED_OR_PD")) {
		rtdm_printk(KERN_ALERT "GPIO requests failed.\n");
		return -ENOMEM;
	}

	gpio_direction_output(GPIO_LED_OR_PD, GPIOF_INIT_LOW);

	if (gpio_request(SPI_CLC, "SPI_CLC")
			|| gpio_request(SPI_MISO, "SPI_MISO")
			|| gpio_request(SPI_MOSI, "SPI_MOSI")
			|| gpio_request(SPI_CS, "SPI_CS")) {
		rtdm_printk(KERN_ALERT "SPI requests failed.\n");
		return -ENOMEM;
	}

	gpio_direction_output(SPI_CLC, GPIOF_INIT_LOW);
	gpio_direction_input(SPI_MISO);
	gpio_direction_output(SPI_MOSI, GPIOF_INIT_LOW);
	gpio_direction_output(SPI_CS, GPIOF_INIT_LOW);

	gpio1 = ioremap(ADDR_BASE_0, 4);
	gpio2 = ioremap(ADDR_BASE_1, 4);

	rtdm_timer_init(&timer, sensing_handler, "sensing");

	mmap_file = debugfs_create_file(MMAP_FILE, 0644, NULL, NULL, &mmap_fops);
	data = (struct data *) kmalloc(sizeof(struct data), GFP_KERNEL);

	rtdm_printk("receive light kernel module loaded\n");
	return 0;
}

void cleanup_module(void) {
	debugfs_remove(mmap_file);
	rtdm_timer_destroy(&timer);
	netlink_kernel_release(sock);
	iounmap(gpio1);
	iounmap(gpio2);
	gpio_free(GPIO_LED_OR_PD);
	gpio_free(SPI_CLC);
	gpio_free(SPI_MISO);
	gpio_free(SPI_MOSI);
	gpio_free(SPI_CS);
	kfree(data);
	rtdm_printk("receive light kernel module unloaded\n");
}

MODULE_LICENSE("GPL");
