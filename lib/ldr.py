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