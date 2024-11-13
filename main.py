from lib.dcmotor import DCMotor
from lib.ldr import LDR
from lib.rgb import RGB
from lib.serial import Serial
from lib.servo import Servo
from time import sleep
from machine import Pin

# PINS
LED = 0
RGB_R = 1
RGB_G = 2
RGB_B = 4
SERVO = 6
SW = 9
ENA = 13
ENB = 15
TX = 16
RX = 17
LDR_PIN = 28

led = Pin(LED, Pin.OUT)
rgb = RGB(RGB_R, RGB_G, RGB_B)
servo = Servo(SERVO)
switch = Pin(SW, Pin.IN)
motor1 = DCMotor(ENA)
motor2 = DCMotor(ENB)
serial = Serial(0, TX, RX)
ldr = LDR(LDR_PIN)