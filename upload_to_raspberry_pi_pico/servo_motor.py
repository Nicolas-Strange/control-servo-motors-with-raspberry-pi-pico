from utime import sleep_us
from machine import Pin, PWM


class ServoController:
    """ core class to control a servo motor with the Raspberry Pi Pico"""

    def __init__(self, signal_pin: int, freq: int = 50, **conf):
        """
        init function
        :param signal_pin: GPIO number where the signal of the servo is plugged (yellow wire)
        :param freq: frequency of the PWM (Pulse Width Modulation) in Hz (50 by default)
        """
        self._servo = PWM(Pin(signal_pin))
        self._servo.freq(freq)

        self._max_angle = conf.get("max_angle", 180)  # maximum operating angle
        self._min_duty = conf.get("min_duty", 1500)  # minimum value of the duty cycle
        self._max_duty = conf.get("max_duty", 7500)  # maximum value of the duty cycle

        self._min_speed = conf.get("min_speed_d_s", 0)  # min speed of the servo
        self._max_speed = conf.get("max_speed_d_s", 600)  # maximum speed of the servo
        self._speed_config = conf.get("speed_config", {})
        self._max_step = max([int(i) for i in self._speed_config.keys()])

        self._current_angle = 0
        self.go_to_position(angle=0, percent_speed=100)
        sleep_us(10 ** 6)

    def go_to_position(self, angle: int, percent_speed: float) -> tuple:
        """
        To set the position of the servo in degrees, we have set up the position with 0 corresponding to the middle,
        positive angles to clockwise rotation, and negative angles to counterclockwise rotation.
        For example, if the servo can rotate 180 degrees, the middle will be 0, the maximum position on the right
        will be 90 degrees, and the maximum position on the left will be -90 degrees.
        :param angle: position in degree
        :param percent_speed: percentage of the maximum rotation speed
        """

        # range the value of angle between -90 and 90
        angle = max(-self._max_angle / 2, angle)
        angle = min(self._max_angle / 2, angle)

        value_start = self._angle_to_duty(angle=self._current_angle)
        value_end = self._angle_to_duty(angle=angle)

        step, waiting_time = self._get_variable_set(percent_speed)
        increment = step if value_end - value_start > 0 else -step

        self._current_angle = angle

        if abs(increment) > abs(value_end - value_start):
            self._servo.duty_u16(value_end)
            return waiting_time, step

        for value in range(value_start, value_end, increment):
            self._servo.duty_u16(value)
            sleep_us(waiting_time)

        return waiting_time / (10 ** 6), step

    def release(self) -> None:
        """ release the PWM """
        self._servo.deinit()

    def _angle_to_duty(self, angle: int) -> int:
        """ convert the angle to duty cycle """
        return int(((self._max_angle // 2) - angle) *
                   (self._max_duty - self._min_duty) / self._max_angle + self._min_duty)

    def _get_variable_set(self, percent_speed: float) -> tuple:
        """ calculate the best parameter set to rotate the servo at the desired speed """
        percent_speed = min(100., percent_speed)
        percent_speed = max(0., percent_speed)

        speed = self._min_speed + percent_speed * (self._max_speed - self._min_speed) / 100

        for step in range(1, self._max_step + 1, 1):
            step = str(step)
            max_speed = self._speed_config[step]["max_speed"]
            min_speed = self._speed_config[step]["min_speed"]
            if min_speed <= speed <= max_speed:
                params = self._speed_config[step]["params"]

                # When we ran the regression, we multiplied the waiting time by 1000 to facilitate better convergence
                # of the model. Additionally, since the waiting time must be in microseconds,
                # we need to divide it by 1000 and then multiply by 10 ** 6, resulting in a final
                # multiplication by 1000.
                waiting_time = (params[0] / (speed - params[1])) * 1000

                return int(step), int(round(waiting_time, 1))
