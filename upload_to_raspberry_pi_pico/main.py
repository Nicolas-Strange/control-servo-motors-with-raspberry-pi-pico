import json

import utime

from servo_motor import ServoController


class Main:
    """ main class that will handle the loop """
    SERVO_NAME = "servo_sg9"

    min_val_inc = -90
    max_val_inc = 90

    def __init__(self):
        """
        init function
        """
        # load the servo conf
        with open("params/servo_params.json") as infile:
            self._conf = json.load(infile)

        self._servo = ServoController(signal_pin=0, **self._conf[self.SERVO_NAME])

    def _run(self, percent_speed: float) -> None:
        """ run one epoch """
        self._servo.go_to_position(angle=self.max_val_inc, percent_speed=percent_speed)

        utime.sleep(2)
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


if __name__ == '__main__':
    run = Main()
    run.run()
