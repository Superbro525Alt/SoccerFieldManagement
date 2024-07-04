import network
import socket
import select
import time
from machine import UART

# Setup WiFi access point
ssid = 'RPiPico-AP'
password = '123456789'
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)

# Setup server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))
server_socket.listen(5)
server_socket.setblocking(False)

# Setup UART for serial communication
uart = UART(0, baudrate=9600, tx=0, rx=1)

# GPS data storage
gps_data = {
    'red_team': [],
    'blue_team': [],
    'ball': None
}
device_counter = {'red_team': 0, 'blue_team': 0, 'ball': 0}

def collate_data():
    """
    Collates data from GPS devices and sends it over UART
    """
    data_str = "GPS Data:\n"
    
    for team in ['red_team', 'blue_team']:
        for player in gps_data[team]:
            data_str += f"{team},{player['id']},{player['lat']},{player['lon']}\n"
    
    if gps_data['ball']:
        data_str += f"ball,{gps_data['ball']['lat']},{gps_data['ball']['lon']}\n"
    
    uart.write(data_str)

def handle_client(client_socket):
    """
    Handles the incoming data from the client
    """
    try:
        data = client_socket.recv(1024)
        if not data:
            return False

        message = data.decode('utf-8').strip().split(',')
        
        if message[0] == 'request_id':
            device_type = message[1]
            device_id = device_counter[device_type]
            device_counter[device_type] += 1
            client_socket.send(f"assigned_id,{device_id}\n".encode('utf-8'))
            return True
        
        device_type, device_id, lat, lon = message[0], int(message[1]), float(message[2]), float(message[3])
        
        if device_type == 'ball':
            gps_data['ball'] = {'lat': lat, 'lon': lon}
        else:
            existing = next((item for item in gps_data[device_type] if item['id'] == device_id), None)
            if existing:
                existing['lat'] = lat
                existing['lon'] = lon
            else:
                gps_data[device_type].append({'id': device_id, 'lat': lat, 'lon': lon})
        
        return True
    except Exception as e:
        print(f"Error handling client: {e}")
        return False

clients = []

while True:
    readable, _, _ = select.select([server_socket] + clients, [], [], 0.1)
    
    for sock in readable:
        if sock is server_socket:
            client_socket, _ = server_socket.accept()
            clients.append(client_socket)
        else:
            if not handle_client(sock):
                sock.close()
                clients.remove(sock)
    
    collate_data()
    time.sleep(0.5)
