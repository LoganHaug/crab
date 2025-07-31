import bluetooth
import pygame

import time
from math import sqrt, floor

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
    if abs(stick_val) > 0.23: return stick_val
    return 0

# max min of each servo
ang_limits = {
        0: (150, 500),
        1: (150, 600),
        2: (150, 600),
        3: (150, 450),
        4: (150, 600),
        5: (150, 600),
        6: (150, 460),
        7: (150, 600),
        8: (150, 600),
        9: (150, 500),
        10: (150, 600),
        11: (150, 600),
        15: (150, 600)
}
def packet_gen(serv, ang) -> str:
    if serv < 0 or serv > 15:
        raise IndexError("invalid servo number")
    if ang < ang_limits[serv][0] or ang > ang_limits[serv][1]:
        raise ValueError("invalid angle")
    return "#".encode() + serv.to_bytes(1, "big") + "+".encode() + ang.to_bytes(2, "big") + "$".encode()

with open("mac.txt", "r") as f:
    esp_mac = f.readline().strip() 
sock = None
try:
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((esp_mac, 1))
    time.sleep(2)
except bluetooth.btcommon.BluetoothError as e:
    print(f"Error: {e}")

controller = None
mode = "crab"
move_vect = [0, 0] # x, y
height = 0
z_dir = 0
test_ang = 375 
last_pack = None
test_ang2 = 90
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            controller = pygame.joystick.Joystick(event.device_index)
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
        if controller is not None:
            # TODO movement code: raise / lower, joystick movement (left stick), turn (right stick)
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
                # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger, 3 = right horiz, 4 = right vert, 5 = right trigger
                move_vect[0] = deadzone(controller.get_axis(3))
                move_vect[1] = deadzone(controller.get_axis(1))
                move_vect = normalize(move_vect)
                if move_vect[0] < 0:
                    test_ang -= 1
                    if test_ang < 150:
                        test_ang = 150 
                elif move_vect[0] > 0:
                    test_ang += 1
                    if test_ang > 600:
                        test_ang = 600 
                pack = packet_gen(11, test_ang)
                if pack != last_pack:
                    print(test_ang)
                    sock.send(pack)
                last_pack = pack
