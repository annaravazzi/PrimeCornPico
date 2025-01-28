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
EN_DISK = 13
EN_CV = 15
TX = 16
RX = 17
LDR_PIN = 28

# Constants
DISK_MOTOR_SPEED = 90
CV_MOTOR_SPEED = 85
LASER_THRESHOLD = 15000
TURN_OFF_TIME = 15000
BUTTON_DEBOUNCE_TIME = 500
LDR_DEBOUNCE_TIME = 500
WAIT_SEED = 0.18
# DEFAULT_TIME = 1000

# Codificated messages between Pico and RPi
SET_IDLE = "set_idle"
SET_SYNC = "set_sync"
SET_READY = "set_ready"
SET_PROCESSING = "set_processing"
SET_SAVING = "set_saving"
REGULAR_SEED = "regular"
IRREGULAR_SEED = "irregular"
UNKNOWN_SEED = "unknown"
SEED_DETECTED = "detected"

# States
BOOT = 0
IDLE = 1
SYNC = 2
READY = 3
PROCESSING = 4
SAVING = 5

# Peripherals
led = Pin(LED, Pin.OUT)
rgb = RGB(RGB_R, RGB_G, RGB_B)
servo = Servo(SERVO)
switch = Pin(SW, Pin.IN)
disk_motor = DCMotor(EN_DISK)
cv_motor = DCMotor(EN_CV, freq=8, min_duty=0, max_duty=65535)
serial = Serial(0, TX, RX)
ldr = LDR(LDR_PIN)

# Servo angles
angle = {"reject": 0, "accept": 90, "neutral": 45}

# RGB colors
colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "purple": (255, 0, 255), "off": (0, 0, 0)}
state_colors = {BOOT: "off", IDLE: "red", READY: "purple", PROCESSING: "green", SAVING: "blue"}

# Initialize peripherals
def init(led, rgb, servo, motor1, motor2):
    led.off()
    rgb.color_hex(0, 0, 0)
    rgb.color_hex(255,255,255)
    servo.write_angle(angle["neutral"])
    motor1.stop()
    motor2.stop()

# Change RGB LED color to one of the predefined colors
def rgb_color(rgb, color):
    rgb.color_hex(colors[color][0], colors[color][1], colors[color][2])

# Check if button is pressed (with debouncing)
def button(switch, debounce):
    return (switch.value() == 0) and (ticks_ms() - debounce > BUTTON_DEBOUNCE_TIME)

# Turn on/off both motors
def turn_on_motors(motor1, motor2, speed1, speed2):
    motor1.forward(100)
    motor2.forward(100)
    motor1.forward(speed1)
    motor2.forward(speed2)

def turn_off_motors(motor1, motor2):
    motor1.stop()
    motor2.stop()

# Check if seed is detected by LDR (with debouncing)
def detect_seed(ldr, debounce):
    return (ldr.read() > LASER_THRESHOLD) and (ticks_ms() - debounce > LDR_DEBOUNCE_TIME)

def main():
    sleep(5)
    init(led, rgb, servo, disk_motor, cv_motor)   # Initialize peripherals
    state = BOOT                   # Initial state

    # Timing variables
    timer = 0
    start_time = 0
    button_debounce = 0
    ldr_debounce = 0
    
    while True:
        # Initial state, waiting for RPi to boot and finish initialization
        if state == BOOT:
            read = serial.read()    # Read message from RPi
            if read == SET_IDLE:    # RPi is ready
                print("boot -> idle")  # Print state transition
                state = IDLE            # Change state
                rgb_color(rgb, state_colors[state])  # Change RGB LED color

        # Idle state
        elif state == IDLE:
            read = serial.read()            # Read message from RPi
            if read == SET_SYNC:         # RPi connected to phone via Bluetooth
                print("idle -> sync")    # Print state transition
                state = SYNC            # Change state
                led.on()                # Turn on connection LED
            elif button(switch, button_debounce):
                button_debounce = ticks_ms()    # Reset button debounce timer
                turn_on_motors(disk_motor, cv_motor, DISK_MOTOR_SPEED, CV_MOTOR_SPEED)  # Turn on DC motors
                serial.write(SET_READY)         # Send message to RPi
                print("idle -> ready")          # Print state transition
                state = READY                   # Change state
                rgb_color(rgb, state_colors[state])  # Change RGB LED color
                # Start timer to turn off motors if no seed is detected
                start_time = ticks_ms()
                timer = 0

        # Waiting for RPi to finish sending data via Bluetooth
        elif state == SYNC:
            read = serial.read()    # Read message from RPi
            if read == SET_IDLE:    # RPi finished sending data
                print("sync -> idle")   # Print state transition
                state = IDLE            # Change state
                led.off()               # Turn off connection LED

        # Waiting for the first seed to be detected
        elif state == READY:
            timer = ticks_ms() - start_time   # Update timer
            if detect_seed(ldr, ldr_debounce):
                print("Seed detected")
                ldr_debounce = ticks_ms()   # Reset LDR debounce timer
                sleep(WAIT_SEED)                  # Wait for seed to be placed correctly
                servo.write_angle(angle["neutral"])  # Set servo to neutral position
                # servo.write_angle(angle["reject"])  # Default
                serial.write(SET_PROCESSING)    # Send message to RPi
                print("ready -> processing")    # Print state transition
                state = PROCESSING              # Change state
                rgb_color(rgb, state_colors[state])  # Change RGB LED color
                # Start timer to turn off motors if no seed is detected
                start_time = ticks_ms()
                timer = 0
            elif button(switch, button_debounce) or (timer > TURN_OFF_TIME):
                button_debounce = ticks_ms() # Reset button debounce timer
                turn_off_motors(disk_motor, cv_motor)           # Turn off DC motors
                serial.write(SET_IDLE)      # Send message to RPi
                print("ready -> idle")      # Print state transition
                state = IDLE                # Change state
                rgb_color(rgb, state_colors[state])  # Change RGB LED color

        elif state == PROCESSING:
            read = serial.read()        # Read message from RPi
            timer = ticks_ms() - start_time     # Update timer
            # Redirect seed
            if read == REGULAR_SEED:
                servo.write_angle(angle["accept"])  # Accept seed
            elif read == IRREGULAR_SEED or read == UNKNOWN_SEED:
                servo.write_angle(angle["reject"])  # Reject seed
                
            # if timer > DEFAULT_TIME:
            #     servo.write_angle(angle["reject"])

            # Laser detected seed
            if detect_seed(ldr, ldr_debounce):
                ldr_debounce = ticks_ms()   # Reset LDR debounce timer
                # Reset timer and start new timer to turn off motors if no seed is detected
                timer = 0
                start_time = ticks_ms()
                sleep(WAIT_SEED)                  # Wait for seed to be placed correctly
                serial.write(SEED_DETECTED)   # Send message to RPi
                print("Seed detected")
            elif timer > TURN_OFF_TIME:
                turn_off_motors(disk_motor, cv_motor)               # Turn off DC motors
                serial.write(SET_SAVING)    # Send message to RPi
                print("processing -> saving")   # Print state transition
                state = SAVING                  # Change state
                rgb_color(rgb, state_colors[state])      # Change RGB LED color
        
        # RPi is saving the data
        elif state == SAVING:
            read = serial.read()    # Read message from RPi
            if read == SET_IDLE:    # RPi finished saving data
                sleep(2)
                print("saving -> idle") # Print state transition
                state = IDLE            # Change state
                rgb_color(rgb, state_colors[state]) # Change RGB LED color

if __name__ == "__main__":
    main()