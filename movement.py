import math

l1 = 0
l2 = 0

def solve_planar_kinematics(x: float, y: float) -> tuple(float, float):
    """Solves the vertical planar 2 link open chain inverse kinematics for the 2nd, 3rd, servos
    x and y is the point in the vertical plane (in mm) to move the end effector to
    returns a tuple of (theta1, and theta2) (in radians) joint angles"""
    alpha = math.acos((x**2 + y**2 + l1**2 - l2**2) / (2 * l1 * l2))
    beta = math.acos((l1**2 + l2**2 - x**2 - y**2) / (2 * l1 * l2))
    gamma = math.acos(x / math.sqrt(x**2 + y**2))
    theta1 = gamma - alpha
    theta2 = math.pi - beta
    return tuple(theta1, theta2)
