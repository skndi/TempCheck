import Adafruit_DHT


def check_data():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
    return temperature, humidity
