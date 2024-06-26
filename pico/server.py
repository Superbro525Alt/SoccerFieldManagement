# server.py
import network
import socket
import ujson as json
import uasyncio as asyncio
import machine
import ubinascii

# Configure the serial connection
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

# Configure WiFi access point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='PicoAP', authmode=network.AUTH_WPA_WPA2_PSK, password='your_password')

clients = {'red_team': {}, 'blue_team': {}, 'ball': {}}

async def handle_client(websocket, path):
    global clients
    async for message in websocket:
        data = json.loads(message)
        if 'red_team' in path:
            clients['red_team'][path] = data
        elif 'blue_team' in path:
            clients['blue_team'][path] = data
        elif 'ball' in path:
            clients['ball'][path] = data
        
        # Collate data from all clients
        collated_data = json.dumps(clients)
        # Send collated data over serial
        uart.write(collated_data + '\n')
        print(f"Sent data over serial: {collated_data}")

async def start_server():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 8765)
    await server.serve_forever()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())

if __name__ == "__main__":
    main()
