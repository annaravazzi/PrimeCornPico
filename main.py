from lib.dcmotor import DCMotor
from lib.ldr import LDR
from lib.rgb import RGB
from lib.serial import Serial
from lib.servo import Servo
from time import sleep, ticks_ms
from machine import Pin

# Pins
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

# Constants
MOTOR1_SPEED = 100
MOTOR2_SPEED = 100
LASER_THRESHOLD = 15000
TURN_OFF_TIME = 15000
BUTTON_DEBOUNCE_TIME = 500
LDR_DEBOUNCE_TIME = 500

# Codificated messages between Pico and RPi
SET_IDLE = "set_idle"
SET_SYNC = "set_sync"
SET_READY = "set_ready"
SET_PROCESSING = "set_processing"
SET_SAVING = "set_saving"
REGULAR = "regular"
IRREGULAR = "irregular"
UNKNOWN = "unknown"
DETECTED = "detected"

# Peripherals
led = Pin(LED, Pin.OUT)
rgb = RGB(RGB_R, RGB_G, RGB_B)
servo = Servo(SERVO)
switch = Pin(SW, Pin.IN)
motor1 = DCMotor(ENA)
motor2 = DCMotor(ENB)
serial = Serial(0, TX, RX)
ldr = LDR(LDR_PIN)

# RGB LED colors
colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "purple": (255, 0, 255), "off": (0, 0, 0)}
state_colors = {"boot": "off", "idle": "red", "ready": "purple", "processing": "green", "saving": "blue"}

# Timing variables
# timer = 0
# start_time = 0
# button_debounce = 0
# ldr_debounce = 0

# Initialize peripherals
def init():
    led.off()
    rgb.color_hex(0, 0, 0)
    servo.write_angle(45)
    motor1.stop()
    motor2.stop()

# Change RGB LED color to one of the predefined colors
def rgb_color(color):
    rgb.color_hex(colors[color][0], colors[color][1], colors[color][2])

# Check if button is pressed (with debouncing)
def button(debounce):
    return (switch.value() == 0) and (ticks_ms() - debounce > BUTTON_DEBOUNCE_TIME)

# Turn on/off both motors
def turn_on_motors(speed1, speed2):
    motor1.forward(speed1)
    motor2.forward(speed2)
def turn_off_motors():
    motor1.stop()
    motor2.stop()

# Check if seed is detected by LDR (with debouncing)
def detect_seed(debounce):
    return (ldr.read() > LASER_THRESHOLD) and (ticks_ms() - debounce > LDR_DEBOUNCE_TIME)

def main():
    init()
    state = "boot"
    timer = 0
    start_time = 0
    button_debounce = 0
    ldr_debounce = 0
    
    while True:
        # Initial state, waiting for RPi to boot and finish initialization
        if state == "boot":
            read = serial.read()
            if read == SET_IDLE:
                print("boot -> idle")
                state = "idle"
                rgb_color(state_colors[state])

        # Idle state
        elif state == "idle":
            read = serial.read()
            # RPi connected to phone via Bluetooth
            if read == SET_SYNC:
                print("idle -> sync")
                state = "sync"
                led.on()
            else:
                # Switch to ready state (turn on DC motors)
                if button(button_debounce):
                    button_debounce = ticks_ms()
                    serial.write(SET_READY)
                    print("idle -> ready")
                    state = "ready"
                    rgb_color(state_colors[state])
                    turn_on_motors(MOTOR1_SPEED, MOTOR2_SPEED)

        # Waiting for RPi to finish sending data via Bluetooth
        elif state == "sync":
            read = serial.read()
            if read == SET_IDLE:
                print("sync -> idle")
                state = "idle"
                led.off()

        # Waiting for the first seed to be detected (user inserting the seeds)
        elif state == "ready":
            if detect_seed(ldr_debounce):
                ldr_debounce = ticks_ms()
                serial.write(SET_PROCESSING)
                print("ready -> processing")
                state = "processing"
                rgb_color(state_colors[state])
                start_time = ticks_ms()
                timer = 0
            else:
                # Return to idle
                if button(button_debounce):
                    button_debounce = ticks_ms()
                    serial.write(SET_IDLE)
                    print("ready -> idle")
                    state = "idle"
                    turn_off_motors()
                    rgb_color(state_colors[state])

        elif state == "processing":
            read = serial.read()

            # Redirect seed
            if read == REGULAR:
                print("regular")
                servo.write_angle(90)
            elif read == IRREGULAR or read == UNKNOWN:
                print("irregular or unknown")
                servo.write_angle(0)
            
            # Laser detected seed
            if detect_seed(ldr_debounce):
                ldr_debounce = ticks_ms()
                timer = 0
                start_time = ticks_ms()     # Reset timer
                print("Seed detected")
                serial.write(DETECTED)
            else:
                timer = ticks_ms() - start_time
                # 15s of inactivity, turn off motors
                if timer > TURN_OFF_TIME:
                    serial.write(SET_SAVING)
                    print("processing -> saving")
                    state = "saving"
                    turn_off_motors()
                    rgb_color(state_colors[state])
        
        # RPi is saving the data
        elif state == "saving":
            read = serial.read()
            if read:
                print(read)
            if read == SET_IDLE:
                print("saving -> idle")
                state = "idle"
                rgb_color(state_colors[state])

if __name__ == "__main__":
    main()