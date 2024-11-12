from machine import Pin, PWM

class RGB:
    def __init__(self, red, green, blue, freq=1000):
        self.red = PWM(Pin(red), freq=freq)
        self.green = PWM(Pin(green), freq=freq)
        self.blue = PWM(Pin(blue), freq=freq)
    
    def color_duty_cycle(self, r, g, b):
        self.red.duty_u16(r)
        self.green.duty_u16(g)
        self.blue.duty_u16(b)

    def color_hex(self, r, g, b):
        self.red.duty_u16(int(r * 65535 / 255))
        self.green.duty_u16(int(g * 65535 / 255))
        self.blue.duty_u16(int(b * 65535 / 255))
    
    def deinit(self):
        self.red.deinit()
        self.green.deinit()
        self.blue.deinit()