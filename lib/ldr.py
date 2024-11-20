from machine import Pin, ADC

class LDR:
    def __init__ (self, pin):
        self.analog_pin = ADC(Pin(pin))
        self.digital_pin = Pin(pin, Pin.IN)
    
    def read(self, analog=True):
        if analog:
            return self.analog_pin.read_u16()
        else:
            return self.digital_pin.value()

if __name__ == "__main__":
    from time import sleep
    ldr = LDR(28)
    led = Pin(15, Pin.OUT)
    led.value(0)
    while True:
        # print(ldr.read())
        if ldr.read() > 15000:
            led.value(1)
        else:
            led.value(0)