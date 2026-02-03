# /main.py
from network import WLAN
import socket
from machine import Pin, idle

board_led = Pin("LED", Pin.OUT, value=0) # Used for indicating listening
led = Pin(2, Pin.OUT, value=0) # The LED used for interfacing

# Setup WLAN
wlan = WLAN()
#
#wlan.active(True)
#wlan.connect("SSID", "PASSWORD")
#
#while not wlan.isconnected():
#    idle()

# Setup socket
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet protocol, UDP
soc.bind(("0.0.0.0", 12345)) # Bind the socket to the machines own IP, and port 12345

print(f'Listening for UDP on {wlan.ipconfig('addr4')[0]}:12345')

# Indicate program is ready
board_led.on()

try:
    while True:
        # Wait for a command
        data, addr = soc.recvfrom(1024)

        print("Received from", addr, ":", data)

        # Convert data from bytes to string
        data = data.decode('ascii').strip('\n').lower()

        # Handle command
        if data == 'toggle':
            led.toggle()
        elif data == 'on':
            led.on()
        elif data == 'off':
            led.off()

except Exception as e:
    # If the program is interrupted, we need to close the port
    soc.close()
    board_led.off()
    raise e # Re-raise the error, so the program exits properly
