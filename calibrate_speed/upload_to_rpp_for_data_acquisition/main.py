import json
import utime

from servo_motor_for_analysis import ServoController


class Main:
    """ main class that will handle the loop """
    FILE_NAME = "time_analysis_servo_raspberry_pico"
    SERVO_NAME = "servo_1"
    MAX_SPEED = 600

    min_val_inc = -90
    max_val_inc = 90

    def __init__(self):
        """
        init function
        """
        with open("./params/servo_params.json") as infile:
            self._conf = json.load(infile)

        self._servo = ServoController(signal_pin=0, **self._conf[self.SERVO_NAME])

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the motion value will be read
        """

        try:
            self._init_position()

            with open(f'{self.FILE_NAME}.csv', 'w') as fd:
                fd.write('rotation_speed(°/s),steps,waiting_time(s)\n')

            for step in range(1, 20):
                for sleep_tm in range(0, 100, 5):
                    start_time = utime.ticks_us()
                    waiting_time = \
                        self._servo.go_to_position(angle=self.max_val_inc, percent_waiting=sleep_tm, steps=step)
                    end_time = utime.ticks_us()
                    time_proc = utime.ticks_diff(end_time, start_time) / (10 ** 6)
                    rotation_speed = 180 / time_proc

                    self._append_file(f"{rotation_speed},{step},{waiting_time}")

                    print(f"rotation_speed(°/s): {rotation_speed} -- step: {step} -- waiting_time(s) {waiting_time}")

                    self._init_position()

        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()

    def _init_position(self):
        """ initialize the servo position """
        utime.sleep(1)
        self._servo.go_to_position(angle=self.min_val_inc, percent_waiting=100, steps=1)
        utime.sleep(1)

    def _append_file(self, value: str) -> None:
        """ write in a file: append mode """
        with open(f'{self.FILE_NAME}.csv', 'a') as fd:
            fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
