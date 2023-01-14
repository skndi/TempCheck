from pydantic import BaseModel
from .common import SENSOR_SOCKET_NAME
import socket
import json


class SensorOutput(BaseModel):
    temperature: float
    humidity: float


def check_data():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(SENSOR_SOCKET_NAME)
        data = sock.recv(255)
        data = json.loads(data)
        temperature = data[0]
        humidity = data[1]
        return SensorOutput(temperature=temperature, humidity=humidity)
