                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple test for NeoPixels on Raspberry Pi
import threading
import time
import neopixel
import board
from urllib.request import urlopen
import json
from datetime import datetime, timedelta
import math
from Driver import Driver
import pytz
from config import num_pixels, total_track_length
import random

import socket

LIRC_SOCKET = "/var/run/lirc/lircd"

pixel_pin = board.D18
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER
)

time_offset = "2023-09-16T13:03:35.200"
time_format = "%Y-%m-%dT%H:%M:%S.%f"
current_time = datetime.strptime(time_offset, time_format)
increment = timedelta(seconds=1)
distance_traveled = 0
prev_x, prev_y = 0, 0  # Assuming the initial position is the origin
total_track_length = 50000
num_leds = num_pixels
current_led_index = 0

current_mode = "clock"
current_color = (255,255,255)
brightness_before_off = 1.0
mode_before_off = "clock"

def clock_mode():
    cst = pytz.timezone('US/Central')
    OFFSET = num_pixels // 2
    current_time = datetime.now(pytz.utc).astimezone(cst)

    hour = current_time.hour % 12
    minute = current_time.minute
    second = current_time.second
    print((OFFSET - second * (num_pixels // 60)) % num_pixels)
    pixels.fill((0,0,0))
    # Set clock pixels, hour has 3 total pixels
    pixels[(OFFSET - hour * 13) % num_pixels] = (255,0,0)
    pixels[(OFFSET - hour * 13) - 1 % num_pixels] = (255,0,0)
    pixels[(OFFSET - hour * 13 + 1) % num_pixels] = (255,0,0)
    pixels[(OFFSET - int(minute * num_pixels / 60)) % num_pixels] = (0,255,0)
    pixels[(OFFSET - int(second * num_pixels / 60)) % num_pixels] = (0,0,255)
    pixels.show()

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

heat = [0] * num_pixels  # Heat array to track each LED's heat value
def fire(cooling, sparking, speed_delay):
    num_pixels = 60
    global heat

        # Step 1. Cool down every cell a little
    for i in range(num_pixels):
        cooldown = random.randint(0, ((cooling * 10) // num_pixels) + 2)
        heat[i] = max(0, heat[i] - cooldown)

    # Step 2. Heat drifts 'up' and diffuses a little
    for k in range(num_pixels - 1, 1, -1):
        heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) // 3

        # Step 3. Randomly ignite new 'sparks' near the bottom
    if random.randint(0, 255) < sparking:
        y = random.randint(0, 6)
        heat[y] = min(255, heat[y] + random.randint(160, 255))

    # Step 4. Map heat to LED colors
    for j in range(num_pixels):
        set_pixel_heat_color(j, heat[j])
        set_pixel_heat_color(num_leds - 1 - j, heat[j])


        # Show updated colors and wait
    pixels.show()
    time.sleep(speed_delay / 1000.0)

def set_pixel_heat_color(pixel, temperature):
    """Convert heat values to colors and set the pixel color."""
    t192 = round((temperature / 255.0) * 191)
    heatramp = (t192 & 0x3F) * 4  # 0..252

    if t192 > 0x80:  # Hottest
        pixels[pixel] = (255, 255, heatramp)
    elif t192 > 0x40:  # Medium
        pixels[pixel] = (255, heatramp, 0)
    else:  # Coolest
        pixels[pixel] = (heatramp, 0, 0)

def handle_button_press(code):
    global current_mode
    global current_color
    global brightness_before_off
    global mode_before_off
    print(code)
    print(current_mode)
    pixels.fill((0,0,0))

    if code == "BRIGHT_UP":
        pixels.brightness = pixels.brightness + 0.1
    elif code == "BRIGHT_DOWN":
            pixels.brightness = max(0.1, pixels.brightness - 0.1)
    elif code == "OFF":
            if not current_mode == "off":
                mode_before_off = current_mode
                current_mode = "off"
                brightness_before_off = pixels.brightness
                print(f"[OFF] Saving brightness: {brightness_before_off}")
                pixels.brightness = 0
                pixels.show()
    elif code == "ON":
            if current_mode == "off":
                current_mode = mode_before_off
                pixels.brightness = max(0.1,brightness_before_off)
                print(pixels.brightness)
                pixels.show()
    elif code == "R0":
            current_mode = "solid"
            current_color = (255, 0, 0)
    elif code == "R1":
            current_mode = "solid"
            current_color = (255, 15, 15)
    elif code == "R2":
            current_mode = "solid"
            current_color = (152, 76, 20)
    elif code == "R3":
            current_mode = "solid"
            current_color = (255, 128, 0)
    elif code == "R4":
            current_mode = "solid"
            current_color = (255, 255, 0)
    elif code == "1H":
            current_mode = "clock"
    elif code == "2H":
            current_mode = "fire"


def listen_for_buttons():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect("/var/run/lirc/lircd")
        while True:
            data = s.recv(128)
            if data:
                parts = data.decode("utf-8").strip().split()
                if len(parts) >= 3:
                    code = parts[2]
                    print(f"Pressed: {code}")
                    handle_button_press(code)

listener_thread = threading.Thread(target=listen_for_buttons, daemon=True)
listener_thread.start()
while True:


    #listen_for_buttons()
    while True:
        if current_mode == "clock":
            clock_mode()
        elif current_mode == "fire":
            fire(55, 120, 15)
        elif current_mode == "solid":
            pixels.fill(current_color)
            pixels.show()
            time.sleep(0.1)
    #fire(55, 120, 15)
    #clock_mode()
    pixels.show()

    #test_car()
    #rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step















