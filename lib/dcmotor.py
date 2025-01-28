from machine import Pin, PWM

class DCMotor:
    def __init__(self, enable, pin1=None, pin2=None, freq=1000, min_duty=15000, max_duty=65535, max_speed=100):
        # Input pins are optional (if not provided, the motor will only work in one direction)
        if pin1:
            self.pin1 = Pin(pin1, Pin.OUT)
        else:
            self.pin1 = None
        if pin2:
            self.pin2 = Pin(pin2, Pin.OUT)
        else:
            self.pin2 = None
        self.enable = PWM(Pin(enable), freq=freq)
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.max_speed = max_speed

    def forward(self, speed):
        self.speed = speed
        self.enable.duty_u16(self.duty_cycle(self.speed))
        if self.pin1:
            self.pin1.value(1)
        if self.pin2:
            self.pin2.value(0)

    def backwards(self, speed):
        self.speed = speed
        self.enable.duty_u16(self.duty_cycle(self.speed))
        if self.pin1:
            self.pin1.value(0)
        if self.pin2:
            self.pin2.value(1)

    def stop(self):
        self.enable.duty_u16(0)
        if self.pin1:
            self.pin1.value(0)
        if self.pin2:
            self.pin2.value(0)
    
    def deinit(self):
        self.enable.deinit()

    def duty_cycle(self, speed):
        if speed <= 0 or speed > self.max_speed:
            duty_cycle = 0
        else:
            duty_cycle = int(self.min_duty + (self.max_duty - self.min_duty) * (speed / self.max_speed))
        return duty_cycle
    

if __name__ == "__main__":
    from time import sleep
    motor1 = DCMotor(13, min_duty=0, max_duty=65535)
    motor2 = DCMotor(15, freq=8, min_duty=0, max_duty=65535)
    motor1.forward(68)
    motor2.forward(100)
    sleep(0.1)
    motor2.forward(100)
    sleep(0.1)
    # motor2.forward(60)
    # motor1.forward(100)
    # while True:
    #     # motor2.forward(100)
    #     # sleep(0.01)
    #     # motor2.forward(50)
    #     # sleep(1)
    #     speed = input()
    #     if speed == 0:
    #         motor1.stop()
    #     else:
    #         motor1.forward(100)
    #         sleep(0.1)
    #         motor1.forward(int(speed))
    # motor1.stop()
    # motor2.stop()