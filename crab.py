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
except bluetooth.btcommon.BluetoothError:
    print(f"Error: {e}")

pygame.init()
pygame.joystick.init()
controller = None 
selected_servo = 0
move_vect = [0, 0]
print("Selected servo 0")
servos = [movement.Servo(i, sock) for i in range(12)]
wait_next_press = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            controller = pygame.joystick.Joystick(event.device_index)
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
    if controller is not None:
        if controller.get_hat(0)[0] and not wait_next_press:
            selected_servo = movement.constrain(selected_servo, 0, 11, controller.get_hat(0)[0]) 
            print(f"Selected servo {selected_servo}")
            wait_next_press = True
        if not controller.get_hat(0)[0]:
            wait_next_press = False
        if controller.get_button(10):
            exit()
        if controller.get_button(2):
            angs = movement.solve_planar_kinematics(100, 0)
            servos[1].set_ang(servos[1]._rad2pwm(angs[0]))
            servos[2].set_ang(servos[2]._rad2pwm(angs[1]))
        if controller.get_button(3):
            angs = movement.solve_planar_kinematics(200, 0) 
            servos[1].set_ang(servos[1]._rad2pwm(angs[0]))
            servos[2].set_ang(servos[2]._rad2pwm(angs[1]))

        if deadzone(controller.get_axis(3)):
            # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger,
            # 3 = right horiz, 4 = right vert, 5 = right trigger
            move_vect[0] = deadzone(controller.get_axis(0))
            move_vect[1] = deadzone(controller.get_axis(3))
            move_vect = normalize(move_vect)
            servos[selected_servo].relative_ang(int(move_vect[1]))
    pygame.event.pump()
    time.sleep(0.01)
