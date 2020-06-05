obj-m        := send_light_kernel.o
KSRC ?= /lib/modules/$(shell uname -r)/build
EXTRA_CFLAGS := -g -I$(KSRC)/include/xenomai $(ADD_CFLAGS)

all::
	$(MAKE) -C $(KSRC) SUBDIRS=$(PWD) modules

clean::
	$(RM) $(CLEANMOD) *.o *.ko *.mod.c Module*.symvers Module.markers modules.order
	$(RM) -R .tmp* .*.cmd