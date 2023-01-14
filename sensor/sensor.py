import socket
import os
from common import SENSOR_SOCKET_NAME
import logging
import random
import json

logger = logging.getLogger()

if __name__ == "__main__":
    if os.path.exists(SENSOR_SOCKET_NAME):
        os.remove(SENSOR_SOCKET_NAME)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.bind(SENSOR_SOCKET_NAME)
        sock.listen()
        while True:
            conn, address = sock.accept()
            with conn:
                logger.info(f"Connection established with: {address}")
                temperature = random.randint(-30, 50)
                humidity = random.randint(0, 100)
                data = json.dumps([temperature, humidity]).encode()
                conn.send(data)
