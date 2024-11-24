from machine import Pin, UART

class Serial:
    def __init__(self, channel, tx, rx, baudrate=9600, timeout=10):
        self.serial = UART(channel, baudrate=baudrate, tx=Pin(tx), rx=Pin(rx), timeout=timeout)
        # self.serial.init(baudrate=baudrate, timeout=timeout)
    
    def write(self, data):
        self.serial.write(data)
    
    def read(self):
        tmp = self.serial.read()
        if tmp:
            return tmp.decode('utf-8').strip()
        return None
    
if __name__ == "__main__":
    from time import sleep
    serial = Serial(0, 16, 17)
    serial.write(bytes("Hello from Pico\n", 'utf-8'))
    while True:
        read = serial.read()
        if read:
            print(read)
            # print(read.decode('utf-8')) # type: ignore