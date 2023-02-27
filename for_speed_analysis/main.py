import json
import utime

from servo_motor_for_analysis import ServoController


class Main:
    """ main class that will handle the loop """
    SERVO_NAME = "servo_1"

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

        min_val_inc = -90
        max_val_inc = 90
        self._servo.go_to_position(angle=min_val_inc, speed=100, increment_factor=10)

        with open('output.csv', 'w') as fd:
            fd.write('speed(%),time(s),increment,sleep_iter(ms)\n')

        for inc in range(1, 20):
            for sleep_tm in range(0, 100, 5):
                start_time = utime.ticks_us()
                sleep_iter = self._servo.go_to_position(angle=max_val_inc, speed=sleep_tm, increment_factor=inc)
                end_time = utime.ticks_us()
                time_proc = utime.ticks_diff(end_time, start_time) / (10 ** 6)

                sleep_iter = sleep_iter / 1000

                append_file(f"{sleep_tm},{time_proc},{inc},{sleep_iter}")
                print(f"speed: {sleep_tm}% -- time: {time_proc}s -- increment: {inc} -- sleep_iter(ms) {sleep_iter}")
                utime.sleep(1)
                self._servo.go_to_position(angle=min_val_inc, speed=100, increment_factor=1)
                utime.sleep(1)

        self._servo.release()


def append_file(value: str) -> None:
    """ write in a file: append mode """
    with open('output.csv', 'a') as fd:
        fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
