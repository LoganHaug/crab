import bluetooth
import pygame
from numpy import interp

import time
from math import sqrt, floor, pi

import movement


def exit():
    if sock is not None:
        sock.close()
    quit()


def normalize(x: float, y: float) -> tuple[int, int]:
    if x > 0.2:
        x = 1
    elif x < -0.2:
        x = -1
    else:
        x = 0
    if y > 0.2:
        y = 1
    elif y < -0.2:
        y = -1
    else:
        y = 0
    return x, y


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

pygame.init()
pygame.joystick.init()
controller = None
selected_servo = 0
selected_leg = 0
print("Selected servo 0")
servos = [movement.Servo(i, sock) for i in range(12)]
legs = [movement.Leg(servos[i : i + 3]) for i in range(0, 12, 3)]
wait_next_press = False
move_vect = legs[selected_leg].position 
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            controller = pygame.joystick.Joystick(event.device_index)
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
    if controller is not None:
        if controller.get_hat(0)[0] and not wait_next_press:
            selected_servo = movement.constrain(
                selected_servo, 0, 11, controller.get_hat(0)[0]
            )
            selected_leg = selected_servo // 3
            print(f"Selected leg {selected_leg}, servo {selected_servo}")
            move_vect = legs[selected_leg].position
            wait_next_press = True
        if controller.get_hat(0) == (0, 0):
            wait_next_press = False
        if controller.get_hat(0)[1] and not wait_next_press:
            servos[selected_servo].relative_ang(controller.get_hat(0)[1])
            wait_next_press = True
        if controller.get_button(10):
            exit()
        # right joystick handling
        # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger,
        # 3 = right horiz, 4 = right vert, 5 = right trigger
        joy_vect = normalize(deadzone(controller.get_axis(3)), -1 * deadzone(controller.get_axis(4)))
        new_x =  move_vect[0] + 0.3 * joy_vect[0] 
        new_y = move_vect[1] + 0.3 * joy_vect[1]
        print(move_vect)
        try:
            for leg in legs:
                leg.position_foot(new_x, new_y)
            move_vect = (new_x, new_y)
        except Exception as e:
            print(e)

    pygame.event.pump()
    time.sleep(0.01)
