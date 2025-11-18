import math

from numpy import interp

# max min of each servo
ang_limits = {
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


# in mm
l1 = 112.7125
l2 = 169.8625


def solve_planar_kinematics(x: float, y: float) -> tuple[float, float]:
    """Solves the vertical planar 2 link open chain inverse kinematics for the 2nd, 3rd, servos
    x and y is the point in the vertical plane (in mm) to move the end effector to
    returns a tuple of (theta1, and theta2) (in radians) joint angles"""
    alpha = math.acos((x**2 + y**2 + l1**2 - l2**2) / (2 * l1 * math.sqrt(x**2 + y**2)))
    beta = math.acos((l1**2 + l2**2 - x**2 - y**2) / (2 * l1 * l2))
    theta1 = ((5 * math.pi) / 9) - alpha
    theta2 = ((3 * math.pi) / 4) - beta
    return theta1, theta2

def rad2pwm(ang: float, servo: int) -> float:
    """Converts an angle in radians to a pulse width in ms
       ang is the angle in radians
       servo is the servo number (each leg servo has a different mounting angle range)"""
    if servo in [0, 3, 6, 9]:
        return interp(ang, [0, math.pi/4], [ang_limits[servo][0], ang_limits[servo][1]])
    elif servo in [1, 4, 7, 10]:
        return interp(ang, [0, (5*math.pi)/9], [ang_limits[servo][0], ang_limits[servo][1]])
    elif servo in [2, 5, 8, 11]:
        return interp(ang, [0, math.pi/4], [ang_limits[servo][0], ang_limits[servo][1]])
    else:
        raise IndexError("Argument servo number does not match a valid servo")
