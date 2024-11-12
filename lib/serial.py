from machine import Pin, UART

class Serial:
    def __init__(self, channel, tx, rx, baudrate=9600, timeout=1000):
        self.serial = UART(channel, baudrate=baudrate, tx=Pin(tx), rx=Pin(rx))
        self.serial.init(baudrate=baudrate, timeout=timeout)
    
    def write(self, data):
        self.serial.write(bytes(data))
    
    def read(self):
        return self.serial.read().decode()