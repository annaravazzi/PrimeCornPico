# TODO: Debounce button

from lib.dcmotor import DCMotor
from lib.ldr import LDR
from lib.rgb import RGB
from lib.serial import Serial
from lib.servo import Servo
from time import sleep, ticks_ms
from machine import Pin

# PINS
LED = 0
RGB_R = 1
RGB_G = 2
RGB_B = 4
SERVO = 22
SW = 9
ENA = 13
ENB = 15
TX = 16
RX = 17
LDR_PIN = 28
MOTOR1_SPEED = 100
MOTOR2_SPEED = 100
LASER_THRESHOLD = 10000
TURN_OFF_TIME = 15000

led = Pin(LED, Pin.OUT)
led.off()
rgb = RGB(RGB_R, RGB_G, RGB_B)
rgb.color_hex(0, 0, 0)
servo = Servo(SERVO)
switch = Pin(SW, Pin.IN)
motor1 = DCMotor(ENA)
motor2 = DCMotor(ENB)
serial = Serial(0, TX, RX)
ldr = LDR(LDR_PIN)

colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "purple": (255, 0, 255), "off": (0, 0, 0)}
state_colors = {"boot": "off", "idle": "red", "ready": "purple", "processing": "green", "saving": "blue"}
timer = 0
start_time = 0

def rgb_color(color):
    rgb.color_hex(colors[color][0], colors[color][1], colors[color][2])

def button():
    return switch.value() == 0

def turn_on_motors(speed1, speed2):
    motor1.forward(speed1)
    motor2.forward(speed2)

def turn_off_motors():
    motor1.stop()
    motor2.stop()

def detect_seed():
    return ldr.read() > LASER_THRESHOLD

def main():
    state = "boot"

    while True:
        if state == "boot":
            read = serial.read()
            if read == "on":
                state = "idle"
                rgb_color(state_colors[state])

        elif state == "idle":
            read = serial.read()
            if read == "set_sync":
                state = "sync"
                led.on()
            else:
                if button():
                    state = "ready"
                    rgb_color(state_colors[state])
                    turn_on_motors(MOTOR1_SPEED, MOTOR2_SPEED)

        elif state == "sync":
            read = serial.read()
            if read == "set_idle":
                state = "idle"
                led.off()

        elif state == "ready":
            if detect_seed():
                serial.write("set_processing")
                state = "processing"
                rgb_color(state_colors[state])
                start_time = ticks_ms()
                timer = 0
            else:
                if button():
                    state = "idle"
                    turn_off_motors()
                    rgb_color(state_colors[state])

        elif state == "processing":
            read = serial.read()
            if read == "regular":
                servo.write_angle(135)
            elif read == "irregular":
                servo.write_angle(45)
            
            if detect_seed():
                timer = 0
                serial.write("detected")
            else:
                timer = ticks_ms() - start_time
                if timer > TURN_OFF_TIME:
                    serial.write("set_saving")
                    state = "saving"
                    turn_off_motors()
                    rgb_color(state_colors[state])
                else:
                    start_time = ticks_ms()
        
        elif state == "saving":
            read = serial.read()
            if read == "set_idle":
                state = "idle"
                rgb_color(state_colors[state])


if __name__ == "__main__":
    main()