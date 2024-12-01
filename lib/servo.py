# from machine import Pin, PWM

# class Servo:
#     def __init__ (self, pin, max_duty=7864, min_duty=1802, freq=50):
#         self.pwm = PWM(Pin(pin), freq=freq)
#         self.freq = freq
#         self.max_duty = max_duty
#         self.min_duty = min_duty
    
#     def write_angle (self, angle):
#         if angle < 0 or angle > 180:
#             duty = 0
#         else:
#             duty = int(((angle / 180) * (self.max_duty - self.min_duty)) + self.min_duty)
#         self.pwm.duty_u16(duty)

#     def deinit (self):
#         self.pwm.deinit()

# if __name__ == "__main__":
#     from time import sleep
#     servo = Servo(22)
#     servo.write_angle(45)
#     sleep(2)
#     while True:
#         servo.write_angle(0)
#         sleep(2)
#         servo.write_angle(110)
#         sleep(2)
from machine import Pin, PWM
from time import sleep

class Servo:
    def __init__(self, pin, max_duty=7864, min_duty=1802, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)  # Set the PWM frequency
        self.max_duty = max_duty
        self.min_duty = min_duty

    def write_angle(self, angle):
        if angle < 0 or angle > 180:
            print("Error: Angle out of range (0-180 degrees).")
            return
        # Map angle to duty cycle range
        duty = int(((angle / 180) * (self.max_duty - self.min_duty)) + self.min_duty)
        self.pwm.duty_u16(duty)

    def deinit(self):
        self.pwm.deinit()

if __name__ == "__main__":
    servo = Servo(22)
    try:
        servo.write_angle(45)
        sleep(2)
        while True:
            servo.write_angle(0)
            sleep(2)
            servo.write_angle(110)
            sleep(2)
    except KeyboardInterrupt:
        print("Stopping servo control.")
    finally:
        servo.deinit()
