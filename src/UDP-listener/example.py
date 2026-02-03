# src/UDP-listener/example.py
from UDP_listener import UDPListener
from random import randint

# Remember to connect to wifi
# from network import WLAN
# wlan = WLAN(WLAN.IF_STA)
# wlan.active(True)
# if not wlan.isconnected():
#     wlan.connect("SSID", "PASSWORD")
#     while not wlan.isconnected():
#         pass

# Initiate the listener
ul = UDPListener()

def nonsense(cmd, *_):
    print(f"'{bytes([randint(0,127) for _ in range(int(cmd))]).decode('ascii')}'")

# Add custom command
ul.add_command("nonsense", nonsense)

# Add command that prints the input
ul.add_command("prt", print)

try:
    while True:
        print("Received command:",ul.start_listening())
finally:
    del ul

""" Now open a linux terminal and run:
echo "prt Hello!" | nc -u <IP-ADDRESS> <PORT>

    Or:
echo "nonsense 20" | nc -u <IP-ADDRESS> <PORT>
"""