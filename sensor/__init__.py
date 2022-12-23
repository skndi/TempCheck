from pydantic import BaseModel

import Adafruit_DHT


class SensorOutput(BaseModel):
    temperature: float
    humidity: float


def check_data():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
    return SensorOutput(temperature=temperature, humidity=humidity)
