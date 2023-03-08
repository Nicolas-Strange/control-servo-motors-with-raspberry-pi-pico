import json
import utime

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
        try:
            self._servo.go_to_position(angle=90, speed=100, increment_factor=10000)
            
            for i in range(1, 5, 1):
                utime.sleep(1)
                print(i)
            
            self._servo.go_to_position(angle=-90, speed=100, increment_factor=10000)
            
            utime.sleep(1)

        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()


def append_file(value: str) -> None:
    """ write in a file: append mode """
    with open('output.csv', 'a') as fd:
        fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
