import utils.log as log
import localvlc.files as files
from localvlc.testbed_setting import Testbed
from receive_light.light_control import ReceiveLightControl

def run_select_token(led):
    log.activate_file_console(files.file_light_token_receiver)
    light_control = ReceiveLightControl(ReceiveLightControl.Action.select_token,
                                        sampling_interval=led.get_sampling_interval(),
                                        evaluate_home_control=True)
    light_control.start()

def main():
    led = Testbed.Pervasive_LED
    run_select_token(led)

if __name__ == "__main__":
    main()
