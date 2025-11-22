import bluetooth
import pygame
from numpy import interp

import time
from math import sqrt, floor, pi

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
selected_servo = 0
move_vect = [0, 0]
print("Selected servo 0")
servos = [movement.Servo(i, sock) for i in range(12)]
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            controller = pygame.joystick.Joystick(event.device_index)
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
        if controller is not None:
            # turn (right stick)
            if event.type == pygame.JOYHATMOTION and event.value[0]:
                selected_servo = movement.constrain(selected_servo, 0, 11, event.value[0])
                print(f"Selected servo {selected_servo}")
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 10:
                    exit()
            if event.type == pygame.JOYAXISMOTION:
                # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger,
                # 3 = right horiz, 4 = right vert, 5 = right trigger
                move_vect[0] = deadzone(controller.get_axis(0))
                move_vect[1] = deadzone(controller.get_axis(3))
                move_vect = normalize(move_vect)
                servos[selected_servo].relative_ang(int(move_vect[1]))
