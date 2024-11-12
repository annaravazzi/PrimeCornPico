from machine import Pin

class Light:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT)
    
    def on(self):
        self.pin.value(1)
    
    def off(self):
        self.pin.value(0)
    
    def toggle(self):
        self.pin.value(not self.pin.value())