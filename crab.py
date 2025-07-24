import bluetooth

import time

esp_mac = "1C:69:20:94:6E:1E"

try:
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((esp_mac, 1))
    time.sleep(2)
    sock.send("test")
    data = sock.recv(1024)
    print(type(data))
except bluetooth.btcommon.BluetoothError as e:
    print(f"Error: {e}")
sock.close()
