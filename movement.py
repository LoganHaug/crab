import math
import bluetooth

from numpy import interp


# max min of each servo
pwm_limits = {
    0: (300, 490),
    1: (275, 500),
    2: (260, 470),
    3: (270, 480),
    4: (250, 480),
    5: (220, 450),
    6: (290, 480),
    7: (250, 500),
    8: (230, 480),
    9: (290, 480),
    10: (270, 520),
    11: (230, 470),
}

# in radians
ang_limits = {
    0: (0, math.pi / 2),
    1: (0, (5 * math.pi) / 9),
    2: (0, math.pi / 2),
    3: (0, math.pi / 2),
    4: (0, (5 * math.pi) / 9),
    5: (0, math.pi / 2),
    6: (0, math.pi / 2),
    7: (0, (5 * math.pi) / 9),
    8: (0, math.pi / 2),
    9: (0, math.pi / 2),
    10: (0, (5 * math.pi) / 9),
    11: (0, math.pi / 2),
}


# in mm
l1 = 112.7125
l2 = 169.8625


def constrain(x, start: int, end: int, delta: int):
    x += delta
    if x < start:
        return start
    elif x > end:
        return end
    return x


class Servo:
    """represents 1 servo on the bot"""

    def _rad2pwm(self, angle: float) -> float:
        """Converts an angle in radians to a pulse width in ms
        angle is the angle in radians"""
        return interp(angle, [self.min_ang, self.max_ang], [self.min_pwm, self.max_pwm])

    def _pwm2rad(self, pulse_width: float) -> float:
        """Converts a pwm value in ms to angle in radians
        pulse_width is the width of the pulse in ms
        servo is the servo number"""
        return interp(
            pulse_width, [self.min_pwm, self.max_pwm], [self.min_ang, self.max_ang]
        )

    def __init__(self, iden: int, sock: bluetooth.BluetoothSocket):
        if iden < 0 or iden > 11:
            raise IndexError("invalid servo number")
        self.id = iden
        self.min_pwm = pwm_limits[self.id][0]
        self.max_pwm = pwm_limits[self.id][1]
        self.min_ang = ang_limits[self.id][0]
        self.max_ang = ang_limits[self.id][1]
        if self.id in [0, 3, 6, 9]:
            self.pulse = (pwm_limits[self.id][1] + pwm_limits[self.id][0]) // 2
        else:
            self.pulse = pwm_limits[self.id][1]
        self.angle = self._pwm2rad(self.pulse)
        self.sock = sock

    def __str__(self):
        return f"i am servo {iden}"

    def set_ang(self, pulse_width):
        """Sends packet to crab brain of #{servo}+{ang}$"""
        if pulse_width < self.min_pwm or pulse_width > self.max_pwm:
            print(ValueError("invalid angle"))
            return None
        if self.sock is None:
            print("WARN: Connection is closed")
        elif pulse_width != self.pulse:
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

    def relative_ang(self, delta: int):
        """Makes the pulse delta ms longer if able"""
        self.set_ang(constrain(self.pulse, self.min_pwm, self.max_pwm, delta))


def solve_planar_kinematics(x: float, y: float) -> tuple[float, float]:
    """Solves the vertical planar 2 link open chain inverse kinematics for the 2nd, 3rd, servos
    x and y is the point in the vertical plane (in mm) to move the end effector to
    returns a tuple of (theta1, and theta2) (in radians) joint angles"""
    alpha = math.acos((x**2 + y**2 + l1**2 - l2**2) / (2 * l1 * math.sqrt(x**2 + y**2)))
    beta = math.acos((l1**2 + l2**2 - x**2 - y**2) / (2 * l1 * l2))
    theta1 = alpha
    theta2 = ((3 * math.pi) / 4) - beta
    return theta1, theta2
