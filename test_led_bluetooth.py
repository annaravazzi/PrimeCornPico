from machine import Pin
from time import sleep

led = pin = Pin(0, Pin.OUT)
led.value(1)
sleep(1)
led.value(0)