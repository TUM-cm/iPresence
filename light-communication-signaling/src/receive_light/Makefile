obj-m        := receive_light_kernel.o
KSRC ?= /lib/modules/$(shell uname -r)/build
EXTRA_CFLAGS := -g -I$(KSRC)/include/xenomai $(ADD_CFLAGS)

all::
	$(MAKE) -C $(KSRC) SUBDIRS=$(PWD) modules

interface::
	python setup.py build_ext --inplace

control::
	gcc light_control.c -o light_control

publish::
	gcc receive_light_user_mqtt.c -lpaho-mqtt3c -o receive_light_user_mqtt

share::
	gcc receive_light_user.c -o receive_light_user

light_receiver::
	gcc -lm light_receiver.c -o light_receiver
	
clean::
	$(RM) $(CLEANMOD) *.o *.ko *.mod.c *.so Module*.symvers Module.markers modules.order
	$(RM) -R .tmp* .*.cmd
