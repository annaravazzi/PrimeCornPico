from machine import Pin, PWM

class Servo:
    def __init__ (self, pin, max_duty=7864, min_duty=1802, freq=50):
        self.pwm = PWM(Pin(pin), freq=freq)
        self.max_duty = max_duty
        self.min_duty = min_duty
    
    def write_angle (self, angle):
        if angle <= 0 or angle > 180:
            duty = 0
        else:
            duty = int(((angle / 180) * (self.max_duty - self.min_duty)) + self.min_duty)
        self.pwm.duty_u16(duty)

    def deinit (self):
        self.pwm.deinit()