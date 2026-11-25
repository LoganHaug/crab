import bluetooth
import pygame
from numpy import interp
import yaml

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


with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
esp_mac = config["mac"]
sock = None
while sock is None:
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((esp_mac, 1))
        print("Connected to ESP32")
        sock.settimeout(0.01)
        time.sleep(2)
        break
    except bluetooth.btcommon.BluetoothError as e:
            print(f"Error: {e}")
    sock = None

pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((300, 100))
pygame.display.set_caption("Crab Control")
controller = None
selected_servo = 0
selected_leg = 0
print("Selected servo 0")
servos = [movement.Servo(i, sock) for i in range(12)]
legs = [movement.Leg(servos[i : i + 3]) for i in range(0, 12, 3)]
wait_next_press = False
move_vect = legs[selected_leg].position 
if config["control_mode"] == "keyboard":
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYUP:
                if config["move_mode"] == "per_servo":
                    if event.key == pygame.K_d:
                        selected_servo = movement.constrain(selected_servo, 0, 11, 1)
                        print(f"Selected servo {selected_servo}")
                    elif event.key == pygame.K_a:
                        selected_servo = movement.constrain(selected_servo, 0, 11, -1)
                        print(f"Selected servo {selected_servo}")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            exit()
        # capture keyboard input, and move the crab
        if config["move_mode"] == "all_leg":
            if keys[pygame.K_w]:
                for leg in legs:
                    leg.position_foot(leg.position[0], leg.position[1] + 2)
            if keys[pygame.K_s]:
                for leg in legs:
                    leg.position_foot(leg.position[0], leg.position[1] - 2)
            if keys[pygame.K_a]:
                for leg in legs:
                    leg.position_foot(leg.position[0] - 2, leg.position[1])
            if keys[pygame.K_d]:
                for leg in legs:
                    leg.position_foot(leg.position[0] + 2, leg.position[1])
        elif config["move_mode"] == "per_servo":
            if keys[pygame.K_w]:
                servos[selected_servo].relative_ang(1)
            if keys[pygame.K_s]:
                servos[selected_servo].relative_ang(-1)
        try:
            print(sock.recv(512))
        except:
            pass
        time.sleep(0.01)
if config["control_mode"] == "controller":
    while True:
        # hotplug the controller (dualshock 4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.JOYDEVICEADDED:
                controller = pygame.joystick.Joystick(event.device_index)
            if event.type == pygame.JOYDEVICEREMOVED:
                controller = None
        if controller is not None:
            joy_vect = normalize(deadzone(controller.get_axis(3)), -1 * deadzone(controller.get_axis(4)))
            # left right dpad rocker, change servo up or down
            if controller.get_hat(0)[0] and not wait_next_press:             
                selected_servo = movement.constrain(
                    selected_servo, 0, 11, controller.get_hat(0)[0]
                )
                selected_leg = selected_servo // 3
                print(f"Selected leg {selected_leg}, servo {selected_servo}")
                move_vect = legs[selected_leg].position
                wait_next_press = True
            # debounce of left_right dpad rocker
            if controller.get_hat(0) == (0, 0):             
                wait_next_press = False
            if controller.get_hat(0)[1] and not wait_next_press:
                servos[selected_servo].relative_ang(controller.get_hat(0)[1])
                print("test")
                wait_next_press = True
            if controller.get_button(10):
                exit()
            if config["move_mode"] == "all_leg":
                # right joystick handling
                # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger,
                # 3 = right horiz, 4 = right vert, 5 = right trigger
                new_x =  move_vect[0] + 2 * joy_vect[0] 
                new_y = move_vect[1] + 2 * joy_vect[1]
                for leg in legs:
                    if leg.position_foot(new_x, new_y):
                        move_vect = (new_x, new_y)
                    else:
                        print("Out of bounds")
            elif config["move_mode"] == "per_servo":
                servos[selected_servo].relative_ang(joy_vect[0])
            elif config["move_mode"] == "per_link":
                #
                link = servo % 3
                print(link)
                if link == 0:
                    pass


        
        try:
            print(sock.recv(512))
        except:
            pass
        pygame.event.pump()
        time.sleep(0.01)
