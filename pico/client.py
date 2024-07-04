import utime
from micropyGPS import MicropyGPS
import machine
import network
import socket

# Setup WiFi connection
ssid = 'RPiPico-AP'
password = '123456789'
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    utime.sleep(1)

# Setup GPS module
gps_module = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))
time_zone = -3
gps = MicropyGPS(time_zone)

# Connect to server
server_ip = '192.168.4.1'  # Adjust according to your setup
server_port = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, server_port))

device_type = 'red_team'  # 'red_team', 'blue_team', or 'ball'
device_id = None

def request_device_id():
    """
    Requests a device ID from the server.
    """
    global device_id
    sock.send(f"request_id,{device_type}\n".encode('utf-8'))
    data = sock.recv(1024).decode('utf-8').strip()
    if data.startswith('assigned_id'):
        device_id = int(data.split(',')[1])

def convert_coordinates(sections):
    if sections[0] == 0:  # sections[0] contains the degrees
        return None

    # sections[1] contains the minutes
    data = sections[0] + (sections[1] / 60.0)

    # sections[2] contains 'E', 'W', 'N', 'S'
    if sections[2] == 'S':
        data = -data
    if sections[2] == 'W':
        data = -data

    data = '{0:.6f}'.format(data)  # 6 decimal places
    return str(data)

def read_gps():
    while gps_module.any():
        gps.update(chr(gps_module.read(1)[0]))
    
    if gps.latitude[0] and gps.longitude[0]:
        lat = gps.latitude[0] + gps.latitude[1] / 60
        if gps.latitude[2] == 'S':
            lat = -lat
        lon = gps.longitude[0] + gps.longitude[1] / 60
        if gps.longitude[2] == 'W':
            lon = -lon
        return lat, lon
    return None, None

# Request device ID from the server
request_device_id()

while device_id is not None:
    lat, lon = read_gps()
    if lat and lon:
        message = f"{device_type},{device_id},{lat},{lon}\n"
        sock.send(message.encode('utf-8'))
    utime.sleep(1)
