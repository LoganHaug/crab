import bluetooth
import pygame

import time

pygame.init()

def exit():
    sock.close()

with open("mac.txt", "r") as f:
    esp_mac = f.readline().strip() 
try:
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((esp_mac, 1))
    time.sleep(2)
except bluetooth.btcommon.BluetoothError as e:
    print(f"Error: {e}")


controller = None
while True:
    for event in pygame.event.get():
        print(event)
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.JOYDEVICEADDED:
            controller = pygame.joystick.Joystick(event.device_index)
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
        if controller is not None:
            print(controller.get_instance_id())
            # TODO movement code: horse or crab mode, raise / lower, joystick movement (left stick), turn (right stick)

