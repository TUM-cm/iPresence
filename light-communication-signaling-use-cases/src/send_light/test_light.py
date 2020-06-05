import utils.kernel_module as kernel_module
from send_light_user import LightSender
from localvlc.testbed_setting import Testbed

led = Testbed.Directed_LED
test_data = "abcdefghijklmnopqrstuvwxyz0123456789"
kernel_module.remove(kernel_module.SEND_KERNEL_MODULE)
light_sender = LightSender()

#light_sender.set_pattern_series([20000,20000])
#light_sender.set_revert_phases(1)

light_sender.set_data(test_data)
light_sender.set_time_base_unit(led.get_time_base_unit())
light_sender.start()
