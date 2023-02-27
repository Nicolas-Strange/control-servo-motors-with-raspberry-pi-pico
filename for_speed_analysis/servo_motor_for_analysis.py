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
        self._max_angle = conf.get("max_angle", 90)  # maximum operating angle
        self._min_duty = conf.get("min_duty", 1950)  # minimum value of the duty cycle
        self._max_duty = conf.get("max_duty", 8600)  # maximum value of the duty cycle
        self._min_sleep = conf.get("min_sleep_us", 100)  # minimum sleeping time between each iteration
        self._max_sleep = conf.get("max_sleep_us", 4000)  # maximum sleeping time between each iteration
        self._current_angle = 0
        self.go_to_position(angle=self._angle_to_duty(0), speed=100, increment_factor=1)

    def go_to_position(self, angle: int, speed: int, increment_factor: int) -> float:
        """
        To set the position of the servo in degrees, we have set up the position with 0 corresponding to the middle,
        positive angles to clockwise rotation, and negative angles to counterclockwise rotation.
        For example, if the servo can rotate 180 degrees, the middle will be 0, the maximum position on the right
        will be 90 degrees, and the maximum position on the left will be -90 degrees.
        :param angle: position in degree
        :param speed: value between 1 and 100 corresponding to the percent of the maximum speed of the servo
        :param increment_factor: how many times the minimum increment
        """
        # range the value of angle between -90 and 90
        angle = max(-self._max_angle/2, angle)
        angle = min(self._max_angle/2, angle)

        value_start = self._angle_to_duty(angle=self._current_angle)
        value_end = self._angle_to_duty(angle=angle)

        increment = increment_factor if value_end - value_start > 0 else -increment_factor
        sleep_iter = \
            int(round(self._max_sleep - (self._max_sleep - self._min_sleep) * speed / 100 + self._min_sleep, 0))

        self._current_angle = angle
        for value in range(value_start, value_end, increment):
            self._servo.duty_u16(value)
            sleep_us(sleep_iter)

        return sleep_iter

    def release(self) -> None:
        """ release the PWM """
        self._servo.deinit()

    def _angle_to_duty(self, angle: int) -> int:
        """ convert the angle to duty cycle """
        return int(((self._max_angle // 2) - angle) *
                   (self._max_duty - self._min_duty) / self._max_angle + self._min_duty)
