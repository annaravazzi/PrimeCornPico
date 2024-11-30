from machine import Pin
from time import sleep, ticks_ms
from lib.dcmotor import DCMotor
from lib.serial import Serial
from lib.rgb import RGB
from lib.servo import Servo

def servo_test():
    motor_cv = DCMotor(15, freq=100, min_duty=0, max_duty=65535)
    motor_disk = DCMotor(13, min_duty=0, max_duty=65535)
    servo = Servo(22)
    servo.write_angle(45)
    motor_disk.forward(100)
    motor_cv.forward(100)
    sleep(0.1)
    motor_cv.forward(80)
    while True:
        servo.write_angle(0)
        sleep(2)
        servo.write_angle(120)
        sleep(2)

def serial_test():
    serial = Serial(0, 16, 17)
    rgb = RGB(1, 2, 4)
    serial.write(bytes("Hello from Pico\n", 'utf-8'))
    while True:
        read = serial.read()
        print(read)
        if read:
            decoded = read.decode('utf-8').strip() # type: ignore
            if decoded == "set_idle":
                print("Idle")
                rgb.color_hex(255, 0, 0)
            elif decoded == "set_ready":
                print("Ready")
                rgb.color_hex(255, 0, 255)
            elif decoded == "set_processing":
                print("Processing")
                rgb.color_hex(0, 255, 0)
            elif decoded == "set_saving":
                print("Saving")
                rgb.color_hex(0, 0, 255)

def motor_test():
    motor1 = DCMotor(13)
    motor2 = DCMotor(15)
    button = Pin(9, Pin.IN)
    state = "off"
    debounce = 0
    start = ticks_ms()

    while True:
        debounce = ticks_ms()
        if state == "off":
            if button.value() == 0 and debounce - start > 500:
                start = ticks_ms()
                print("Button pressed (on)")
                state = "on"
                motor1.forward(100)
                motor2.forward(100)
                sleep(0.1)
                motor1.forward(30)
                motor2.forward(30)
        if state == "on":
            if button.value() == 0 and debounce - start > 500:
                start = ticks_ms()
                print("Button pressed (off)")
                state = "off"
                motor1.stop()
                motor2.stop()

if __name__ == "__main__":
    # serial_test()
    servo_test()
    # motor_test()