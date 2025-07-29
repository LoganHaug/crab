import bluetooth
import pygame

import time
from math import sqrt

pygame.init()

def exit():
    sock.close()

def normalize(vect: list[float]) -> list[float]:
    length = sqrt(vect[0] ** 2 + vect[1] ** 2)
    if length == 0:
        return [0, 0]
    return [vect[0] / length, vect[1] / length]

def deadzone(stick_val: float) -> float:
    if abs(stick_val) > 0.23: return stick_val
    return 0
"""
with open("mac.txt", "r") as f:
    esp_mac = f.readline().strip() 
try:
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((esp_mac, 1))
    time.sleep(2)
except bluetooth.btcommon.BluetoothError as e:
    print(f"Error: {e}")
"""


controller = None
mode = "crab"
move_vect = [0, 0] # x, y
height = 0
z_dir = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.JOYDEVICEADDED:
            controller = pygame.joystick.Joystick(event.device_index)
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
        if controller is not None:
            # TODO movement code: horse or crab mode, raise / lower, joystick movement (left stick), turn (right stick)
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:
                    if mode == "crab":
                        mode = "dog"
                    else:
                        mode = "crab"
                    print(f"Mode: {mode}")
            if event.type == pygame.JOYAXISMOTION:  
                # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger, 3 = right horiz, 4 = right vert, 5 = right trigger
                move_vect[0] = deadzone(controller.get_axis(0))
                move_vect[1] = deadzone(controller.get_axis(1))
                move_vect = normalize(move_vect)
