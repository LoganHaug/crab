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
        0: (150, 430),
        1: (180, 530),
        2: (150, 320),
        3: (150, 330),
        4: (150, 530),
        5: (250, 500),
        6: (150, 600),
        7: (150, 600),
        8: (150, 600),
        9: (150, 600),
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

def stand_leg(s1: int, s2: int, s3: int) -> bytes:
    yield packet_gen(s1, 375)
    yield packet_gen(s2, 500)
    yield packet_gen(s3, 500)
    yield packet_gen(s2, 400)
    yield packet_gen(s3, 400)

def sit_leg(s1: int, s2: int, s3: int) -> bytes:
    yield packet_gen(s1, 375)
    yield packet_gen(s2, 500)
    yield packet_gen(s3, 500)

def rotate_leg(ang: int, s1: int, s2: int, s3: int, s4: int) -> bytes:
    yield packet_gen(s1, ang)
    if ang > ang_limits[s2][1]:
        yield packet_gen(s2, ang_limits[s2][1])
    else:
        yield packet_gen(s2, ang)

    if ang > ang_limits[s3][1]:
        yield packet_gen(s3, ang_limits[s3][1])
    else:
        yield packet_gen(s3, ang)
    yield packet_gen(s4, ang)

def constrain(x, start, end, delta):
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

controller = None
mode = "crab"
move_vect = [0, 0, 0] # x, y, turn
height = 0
z_dir = 0
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
            # TODO movement code: raise / lower, joystick movement (left stick), turn (right stick)
            if event.type == pygame.JOYHATMOTION:
                servo_num = constrain(servo_num, 0, 11, event.value[0])
                print(f"servo_num: {servo_num}")
                
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:
                    if mode == "crab":
                        mode = "dog"
                    else:
                        mode = "crab"
                    print(f"Mode: {mode}")
                """
                if event.button == 3:
                    packs_l1 = [pack for pack in stand_leg(0, 1, 2)]
                    packs_l2 = [pack for pack in stand_leg(3, 4, 5)]
                    packs_l3 = [pack for pack in stand_leg(6, 7, 8)]
                    packs_l4 = [pack for pack in stand_leg(9, 10, 11)]
                    for pack in range(len(packs_l1)):
                        sock.send(packs_l1[pack])
                        sock.send(packs_l2[pack])
                        sock.send(packs_l3[pack])
                        sock.send(packs_l4[pack])
                        time.sleep(0.5)
                if event.button == 4:
                    packs_l1 = [pack for pack in sit_leg(0, 1, 2)]
                    packs_l2 = [pack for pack in sit_leg(3, 4, 5)]
                    packs_l3 = [pack for pack in sit_leg(6, 7, 8)]
                    packs_l4 = [pack for pack in sit_leg(9, 10, 11)]
                    for pack in range(len(packs_l1)):
                        sock.send(packs_l1[pack])
                        sock.send(packs_l2[pack])
                        sock.send(packs_l3[pack])
                        sock.send(packs_l4[pack])
                        time.sleep(0.5)

                elif event.button == 10:
                    exit()
                    """
            if event.type == pygame.JOYAXISMOTION:  
                # axis index: 0 = left horiz, 1 = left vert, 2 = left trigger, 3 = right horiz, 4 = right vert, 5 = right trigger
                move_vect[0] = deadzone(controller.get_axis(0))
                move_vect[1] = deadzone(controller.get_axis(3))
                move_vect = normalize(move_vect)
                delta = constrain(test_ang, 150, 600, int(move_vect[1]))
                if delta != test_ang:
                    test_ang = delta
                    print(f"test_ang: {test_ang}")
                    pack = packet_gen(servo_num, test_ang)
                    sock.send(pack)

