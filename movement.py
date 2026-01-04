import math

import bluetooth
from numpy import interp


# max min of each servo
pwm_limits = {
    0: (300, 490),
    1: (275, 500),
    2: (260, 470),

    3: (310, 500),
    4: (240, 465),
    5: (220, 440),

    6: (290, 480),
    7: (250, 475),
    8: (230, 450),

    9: (290, 480),
    10: (255, 475),
    11: (230, 430),
}

# in radians
ang_limits = {
    0: (0, math.pi / 2),
    1: (0, (7 * math.pi) / 12),
    2: (0, (19 * math.pi) / 36),
    3: (0, math.pi / 2),
    4: (0, (7 * math.pi) / 12),
    5: (0, (19 * math.pi) / 36),
    6: (0, math.pi / 2),
    7: (0, (7 * math.pi) / 12),
    8: (0, (19 * math.pi) / 36),
    9: (0, math.pi / 2),
    10: (0, (7 * math.pi) / 12),
    11: (0, (19 * math.pi) / 36),
}


# in mm
l1 = 112.5
l2 = 170


def constrain(x, start: int, end: int, delta: int):
    x += delta
    if x < start:
        return start
    elif x > end:
        return end
    return x


class Servo:
    """represents 1 servo on the bot"""

    def _rad2pwm(self, angle: float) -> int:
        """Converts an angle in radians to a pulse width in ms
        angle is the angle in radians"""
        if self.id in [1, 4, 7, 10]:
            return int(
                interp(
                    angle, [self.min_ang, self.max_ang], [self.max_pwm, self.min_pwm]
                )
            )
        return int(
            interp(angle, [self.min_ang, self.max_ang], [self.min_pwm, self.max_pwm])
        )

    def _pwm2rad(self, pulse_width: int) -> float:
        """Converts a pwm value in ms to angle in radians
        pulse_width is the width of the pulse in ms
        servo is the servo number"""
        if self.id in [1, 4, 7, 10]:
            return interp(
                pulse_width, [self.min_pwm, self.max_pwm], [self.max_ang, self.min_ang]
            )
        return interp(
            pulse_width, [self.min_pwm, self.max_pwm], [self.min_ang, self.max_ang]
        )

    def __init__(self, iden: int, sock: bluetooth.BluetoothSocket):
        if iden < 0 or iden > 11:
            raise IndexError("invalid servo number")
        self.id = iden
        self.sock = sock
        self.min_pwm = pwm_limits[self.id][0]
        self.max_pwm = pwm_limits[self.id][1]
        self.min_ang = ang_limits[self.id][0]
        self.max_ang = ang_limits[self.id][1]
        if self.id in [0, 3, 6, 9]:
            self.pulse = (pwm_limits[self.id][1] + pwm_limits[self.id][0]) // 2
        else:
            self.pulse = pwm_limits[self.id][1]
        self.set = False
        self.set_pulse(self.pulse)
        self.angle = self._pwm2rad(self.pulse)

    def __str__(self):
        return f"i am servo {iden}"

    def set_pulse(self, pulse_width: int):
        """Sends packet to crab brain of #{servo}+{1.2086398107282492ang}$"""
        if pulse_width < self.min_pwm or pulse_width > self.max_pwm:
            raise ValueError("invalid pulse")
        if self.sock is None:
            raise bluetooth.BluetoothError("Connection is offline")
        elif pulse_width != self.pulse or not self.set:
            self.pulse = pulse_width
            self.sock.send(
                "#".encode()
                + self.id.to_bytes(1, "big")
                + "+".encode()
                + self.pulse.to_bytes(2, "big")
                + "$".encode()
            )
            self.angle = self._pwm2rad(self.pulse)
            print(f"servo: {self.id}\tpulse: {self.pulse}\tangle: {self.angle}")
            self.set = True

    def relative_ang(self, delta: int):
        """Makes the pulse delta ms longer if able"""
        self.set_pulse(constrain(self.pulse, self.min_pwm, self.max_pwm, delta))


class Leg:
    def __init__(self, servos: list[Servo]):
        self.servos = servos
        self.s0 = self.servos[0]
        self.s1 = self.servos[1]
        self.s2 = self.servos[2]
        self.position = self.get_pos()

    def get_pos(self) -> tuple[float, float]:
        return l1 * math.cos(self.s1.angle) + l2 * math.cos(
            self.s1.angle + self.s2.angle
        ), l1 * math.sin(self.s1.angle) + l2 * math.sin(self.s1.angle + self.s2.angle)

    def position_foot(self, x: float, y: float) -> bool:
        """Solves the vertical planar 2 link open chain inverse kinematics for the 2nd, 3rd, servos, and then moves there
        x and y is the point in the vertical plane (in mm) to move the end effector to
        """
        denominator = 2 * l1 * math.sqrt(x**2 + y**2)
        if abs(denominator) < 0.01:
            raise ValueError("Unreachable position")
        if abs(x) < 0.01:
            alpha = math.acos((l1**2 + x**2 + y**2 - l2**2) / denominator)
        else:
            arg = (l1**2 + x**2 + y**2 - l2**2) / denominator
            if -1 > arg or arg > 1:
                return False
            alpha = math.acos(arg) + math.atan2(y, x)
        denominator = 2 * l1 * l2
        if abs(denominator) < 0.01:
            raise ValueError("Unreachable position")
        beta = math.acos((l1**2 + l2**2 - x**2 - y**2) / denominator)
        theta1 = ((7 * math.pi) / 12) - alpha
        s1pwm = self.s1._rad2pwm(theta1)
        if s1pwm < self.s1.min_pwm or s1pwm > self.s1.max_pwm:
            print("theta1 fail")
            return False
        theta2 = ((3 * math.pi) / 4) - beta
        s2pwm = self.s2._rad2pwm(theta2)
        if s2pwm < self.s2.min_pwm or s2pwm > self.s2.max_pwm:
            print("theta2 fail")
            return False
            print(e)
            
        self.s1.set_pulse(self.s1._rad2pwm(theta1))
        self.s2.set_pulse(self.s2._rad2pwm(theta2))
        self.position = self.get_pos()
        return True
