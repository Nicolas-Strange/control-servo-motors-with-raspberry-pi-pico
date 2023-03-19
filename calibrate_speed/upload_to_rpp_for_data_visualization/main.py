import json
import utime
from machine import Pin

from servo_motor import ServoController


class Main:
    """ main class that will handle the loop """
    FILE_NAME = "data_rotation_results"
    SERVO_NAME = "servo_s53_20"

    min_val_inc = -90
    max_val_inc = 90

    def __init__(self):
        """
        init function
        """
        # load the servo conf
        with open("params/servo_params.json") as infile:
            self._conf = json.load(infile)

        with open(f'{self.FILE_NAME}_{self.SERVO_NAME}.csv', 'w') as fd:
            fd.write('percent_speed,rotation_speed(°/s)\n')

        self._servo = ServoController(signal_pin=0, **self._conf[self.SERVO_NAME])
        self._photo_intercept = Pin(1, Pin.IN, Pin.PULL_UP)

    def _run(self, percent_speed: float) -> None:
        """ run one epoch """
        start_time = utime.ticks_us()
        waiting_time, step = self._servo.go_to_position(angle=self.max_val_inc, percent_speed=percent_speed)

        # While the IR sensor is not activated we wait
        while not self._photo_intercept.value():
            utime.sleep_us(10)

        end_time = utime.ticks_us()
        rotation_time = utime.ticks_diff(end_time, start_time) / (10 ** 6)

        print(
            f"percent_speed: {percent_speed} --- Rotation speed (°/s): {180 / rotation_time} -- waiting_time: {waiting_time} -- step: {step}")

        self._append_file(f"{percent_speed},{180 / rotation_time}")

        self._init_position()

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the motion value will be read
        """
        try:
            self._init_position()

            for percent_speed in range(0, 110, 10):
                self._run(percent_speed=percent_speed)

        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()

    def _init_position(self):
        """ initialize the servo position """
        utime.sleep(1)
        self._servo.go_to_position(angle=self.min_val_inc, percent_speed=100)
        utime.sleep(1)

    def _append_file(self, value: str) -> None:
        """ write in a file: append mode """
        with open(f'{self.FILE_NAME}_{self.SERVO_NAME}.csv', 'a') as fd:
            fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
