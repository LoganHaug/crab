import bluetooth
import pygame
from numpy import interp

import time
from math import sqrt, floor

import movement

pygame.init()


def exit():
    if sock is not None:
        sock.close()
    quit()


def normalize(vect: list[float]) -> list[float]:
    length = sqrt(vect[0] ** 2 + vect[1] ** 2)
    if length == 0:
        return [0, 0]
    return [vect[0] / length, vect[1] / length]


def deadzone(stick_val: float) -> float:
    if abs(stick_val) > 0.23:
        return stick_val
    return 0


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


def packet_gen(serv, ang) -> str:
    if serv < 0 or serv > 15:
        raise IndexError("invalid servo number")
    if ang < ang_limits[serv][0] or ang > ang_limits[serv][1]:
        print(ValueError("invalid angle"))
        return None
    return (
        "#".encode()
        + serv.to_bytes(1, "big")
        + "+".encode()
        + ang.to_bytes(2, "big")
        + "$".encode()
    )


def constrain(x, start: int, end: int, delta: int):
    x += delta
    if x < start:
        return start
    elif x > end:
        return end
    return x


with open("mac.txt", "r") as f:
    esp_mac = f.readline().strip()
sock = None
try:
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((esp_mac, 1))
    time.sleep(2)
except bluetooth.btcommon.BluetoothError as e:
    print(f"Error: {e}")

height = 0
controller = None
mode = "crab"
move_vect = [0, 0, 0]  # x, y, theta
height = 0
test_ang = 375
last_pack = None
servo_num = 0
print(f"servo num: {servo_num}")
print(f"test ang: {test_ang}")
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            controller = pygame.joystick.Joystick(event.device_index)
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
        if controller is not None:
            # TODO movement code: raise / lower, joystick movement (left stick),
            # turn (right stick)
            if event.type == pygame.JOYHATMOTION:
                servo_num = constrain(servo_num, 0, 11, event.value[0])
                test_ang = (ang_limits[servo_num][1] + ang_limits[servo_num][0]) // 2
                print(f"servo_num: {servo_num}, test_ang {test_ang}")
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:
                    if mode == "crab":
                        mode = "dog"
                    else:
                        mode = "crab"
                    print(f"Mode: {mode}")
                elif event.button == 10:
                    exit()
            if event.type == pygame.JOYAXISMOTION:
                # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger,
                # 3 = right horiz, 4 = right vert, 5 = right trigger
                move_vect[0] = deadzone(controller.get_axis(0))
                move_vect[1] = deadzone(controller.get_axis(3))
                move_vect = normalize(move_vect)
                new_ang = int(constrain(test_ang, 150, 600, int(move_vect[1])))
                if new_ang != test_ang:
                    print(f"test_ang: {test_ang}")
                    pack = packet_gen(servo_num, new_ang)
                    try:
                        sock.send(pack)
                        test_ang = new_ang
                    except:
                        print("didnt send")
