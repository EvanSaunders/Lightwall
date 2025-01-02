# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple test for NeoPixels on Raspberry Pi
import time
import neopixel
import board
from urllib.request import urlopen
import json
from datetime import datetime, timedelta
import math


pixel_pin = board.D18
num_pixels = 300
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

time_offset = "2023-09-16T13:03:35.200"
time_format = "%Y-%m-%dT%H:%M:%S.%f"
current_time = datetime.strptime(time_offset, time_format)
increment = timedelta(seconds=1)
distance_traveled = 0
prev_x, prev_y = 0, 0  # Assuming the initial position is the origin
total_track_length = 50000
num_leds = 200
current_led_index = 0
while True:

    next_time = current_time + increment
    time_offset = current_time.strftime(time_format)
    new_time_offset = next_time.strftime(time_format)

    # Reset x_values to hold only current iteration data
    x_values = []  # Clear the list before querying

    # Fetch data for the current time range
    response = urlopen(
        f'https://api.openf1.org/v1/location?session_key=9161&driver_number=81&date>{time_offset}&date<{new_time_offset}'
    )
    data = json.loads(response.read().decode('utf-8'))

    if current_led_index is not None:
        pixels[current_led_index] = (0, 0, 0)  # Turn off the previous LED
    if data:
       # Assuming the list is ordered by time, the last entry should be the most recent
       most_recent_x_value = data[-1]['x']
       #print(f"Most recent X value at {time_offset} to {new_time_offset}: {most_recent_x_value}")
       most_recent_y_value = data[-1]['y']
       #print(most_recent_y_value)


       distance_traveled += math.sqrt((most_recent_x_value - prev_x) ** 2 + (most_recent_y_value - prev_y) ** 2)
       prev_x, prev_y = most_recent_x_value, most_recent_y_value
       #total_track_length = 10000
       #print(most_recent_x_value % 100)
       #print(most_recent_y_value % 100)
       #percentage_completed = (distance_traveled / total_track_length)*100
       #print(percentage_completed)
       led_index = ((distance_traveled % total_track_length) / total_track_length) * num_pixels

       print(led_index)
       pixels[math.floor(led_index)] = (0, 255, 0)  # RGB values for green
       current_led_index = math.floor(led_index)
       # Show the updated LED strip
       pixels.show()
       #time.sleep(1)

    # Wait before polling for new data
    current_time = next_time


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


while True:
    # Comment this line out if you have RGBW/GRBW NeoPixels
    pixels.fill((255, 0, 255))
   # Uncomment this line if you have RGBW/GRBW NeoPixels
   # pixels.fill((255, 0, 0, 0))
    pixels.show()
    #time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
    #pixels.fill((0, 255, 0))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 255, 0, 0))
   # pixels.show()
    time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
    #pixels.fill((0, 0, 255))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 0, 255, 0))
   # pixels.show()
    #time.sleep(1)

    rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step

