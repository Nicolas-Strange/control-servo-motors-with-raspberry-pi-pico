import json
from time import sleep, ticks_us

from servo_motor import ServoController


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
        self._servo.go_to_position(angle=90, speed=100, increment_factor=10)

        with open('output.txt', 'w') as fd:
            fd.write('speed(%),time(s),increment,sleep_iter(s)\n')

        for inc in range(1, 20):
            for sleep_tm in range(10, 100, 5):
                init_time = ticks_us()
                sleep_iter = self._servo.go_to_position(angle=max_val_inc, speed=sleep_tm, increment_factor=inc)
                time_proc = (ticks_us() - init_time) / (10 ** 6)
                append_file(f"{sleep_tm},{time_proc},{inc},{sleep_iter}")
                print(f"speed: {sleep_tm}% -- time: {time_proc}s -- increment: {inc} -- sleep_iter {sleep_iter}")
                sleep(1)
                self._servo.go_to_position(angle=min_val_inc, speed=100, increment_factor=1)
                sleep(1)

        self._servo.release()


def append_file(value: str) -> None:
    """ write in a file: append mode """
    with open('output.txt', 'a') as fd:
        fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
