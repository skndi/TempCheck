import random

from pydantic import BaseModel


# import Adafruit_DHT


class SensorOutput(BaseModel):
    temperature: float
    humidity: float


def check_data():
    # humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
    temperature, humidity = random.Random().randint(0, 10000) / 100, random.Random().randint(5000, 10000) / 100
    return SensorOutput(temperature=temperature, humidity=humidity)
