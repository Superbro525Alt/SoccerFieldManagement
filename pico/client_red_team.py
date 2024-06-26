# client_red_team.py
import network
import usocket as socket
import uasyncio as asyncio
import ujson as json
from machine import UART, Pin

# Connect to the WiFi access point
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect('PicoAP', 'your_password')

while not sta.isconnected():
    pass

print('Connected to WiFi:', sta.ifconfig())

# Configure the GPS module
gps_uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

async def connect_to_server():
    url = 'ws://192.168.4.1:8765/red_team/player1'
    _, _, host, port, path = url.split('/')
    addr_info = socket.getaddrinfo(host, int(port))
    addr = addr_info[0][-1]
    
    sock = socket.socket()
    sock.connect(addr)
    websocket = await asyncio.start_client(sock)
    
    return websocket

async def send_gps_data():
    websocket = await connect_to_server()
    
    while True:
        if gps_uart.any():
            line = gps_uart.readline().decode('utf-8')
            if "$GPGGA" in line:
                data = parse_gpgga(line)
                if data:
                    message = json.dumps(data)
                    await websocket.send(message)
                    print(f"Sent GPS data: {data}")
        await asyncio.sleep(1)

def parse_gpgga(line):
    parts = line.split(',')
    if len(parts) < 15:
        return None
    
    try:
        lat = float(parts[2])
        lon = float(parts[4])
        
        lat_dir = parts[3]
        lon_dir = parts[5]
        
        if lat_dir == 'S':
            lat = -lat
        if lon_dir == 'W':
            lon = -lon
        
        return {
            'lat': lat,
            'lon': lon,
            'fix_quality': int(parts[6]),
            'num_satellites': int(parts[7]),
            'horizontal_dilution': float(parts[8]),
            'altitude': float(parts[9])
        }
    except ValueError:
        return None

async def main():
    await send_gps_data()

if __name__ == "__main__":
    asyncio.run(main())

