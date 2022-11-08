import websockets
import threading
import asyncio
import time
import os
import json
import sys

sensor_data = {} # Dict that stores values per sensor (per id)
output_dir = sys.argv[1]

def write_to_file(sensor_id, output_dir):
    global sensor_data
    with open(os.path.join(output_dir, "{}.json".format(sensor_id)), 'w') as ofile:
        json.dump(sensor_data[sensor_id], ofile)

async def start_ws_listener():
    global sensor_data
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = json.loads(await websocket.recv())
            if not msg is None:
                sensor_id = int(msg['extendedDeviceID'])
                if sensor_id not in sensor_data:
                    sensor_data[sensor_id]=[]
                sensor_data[sensor_id].append(msg)
                threading.Thread(target=write_to_file, args=(sensor_id, output_dir,)).start()
            time.sleep(0.0001)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(start_ws_listener())
