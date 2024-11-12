from machine import Pin, PWM

class DCMotor:
    def __init__(self, pin1, pin2, enable, min_duty=15000, max_duty=65535, max_speed=100):
        self.pin1 = Pin(pin1, Pin.OUT)
        self.pin2 = Pin(pin2, Pin.OUT)
        self.enable = PWM(Pin(enable))
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.max_speed = max_speed

    def forward(self, speed):
        self.speed = speed
        self.enable.duty_u16(self.duty_cycle(self.speed))
        self.pin1.value(1)
        self.pin2.value(0)

    def backwards(self, speed):
        self.speed = speed
        self.enable.duty_u16(self.duty_cycle(self.speed))
        self.pin1.value(0)
        self.pin2.value(1)

    def stop(self):
        self.enable.duty_u16(0)
        self.pin1.value(0)
        self.pin2.value(0)
    
    def deinit(self):
        self.enable.deinit()

    def duty_cycle(self, speed):
        if speed <= 0 or speed > self.max_speed:
            duty_cycle = 0
        else:
            duty_cycle = int(self.min_duty + (self.max_duty - self.min_duty) * (speed / self.max_speed))
        return duty_cycle