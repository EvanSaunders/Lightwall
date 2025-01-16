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
from Driver import Driver
import pytz
from config import num_pixels, total_track_length
import random

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

def calculate_led_index(distance_traveled, total_track_length, num_pixels):
    return ((distance_traveled % total_track_length) / total_track_length) * num_pixels

def hex_to_rgb(hex_color):
    print("hex_called")
    # If the input is an integer, convert it to a hex string
    if isinstance(hex_color, int):
        print("working")
        print(hex_color)
        hex_color = f"{hex_color:06X}"  # Ensure it's a 6-character string, uppercase
        print(hex_color)

    # Remove '#' if it's included in the hex string (e.g., "#3671C6")
    hex_color = hex_color.lstrip('#')

    # Ensure it's a valid hex color string with 6 characters
    if len(hex_color) != 6 or not all(c in '0123456789ABCDEF' for c in hex_color.upper()):
        raise ValueError("Invalid hex color format")

    # Return a tuple of RGB values by slicing the hex string
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def fetch_and_display_past_session():
    start_time = "2023-09-17T12:00:00.000"
    end_time = "2023-09-17T13:25:35.200"
    current_led_index = 0
    driver_number_list = [1,4,81,44, 31, 10, 22, 77, 55]
    driver_list = []
    for driver in driver_number_list:


        #get driver team colors
        response = urlopen(f'https://api.openf1.org/v1/drivers?driver_number={driver}&session_key=9165')
        colour_data = json.loads(response.read().decode('utf-8'))
        #print(colour_data)
        #get driver locations for session
        response = urlopen(
        f'https://api.openf1.org/v1/location?session_key=9165&driver_number={driver}&date>{start_time}&date<{end_time}'
        )
        location_data = json.loads(response.read().decode('utf-8'))
        if colour_data and location_data:
            driver_locations = [(item['x'], item['y']) for item in location_data]  # Extract x, y coordinates
            driver_colour = colour_data[0]['team_colour']  # Store the team's color for the driver
            print(driver_colour)
            # Create the Driver object and append it to the driver_list
            driver_list.append(Driver(driver, driver_colour, driver_locations))  # Pass driver locations and total_track_length
    while True:
        all_positions_displayed = True  # Check if all drivers are out of positions to display

        for driver in driver_list:  # Iterate through each Driver object in the driver_list
            if driver.locations:  # If there are still locations to display for this driver
                print(driver.get_led_index)
                if current_led_index is not None:
                    pixels[math.floor(driver.current_position)] = (0, 0, 0)
                driver.update_position()
                # Should print a valid hex string or integer
                pixels[driver.get_led_index()] = hex_to_rgb(driver.get_driver_colour())  # RGB values for green
                pixels.show()
                current_led_index = driver.get_led_index()
                all_positions_displayed = False  # Still more positions to display

        if all_positions_displayed:
            break  # Exit the loop if all drivers have no more positions to display

        time.sleep(0.01)  # Delay for a small amount of time before the next update


def clock_mode():
    cst = pytz.timezone('US/Central')
    OFFSET = num_pixels // 2
    while True:
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

def test_car():
    distance_traveled = 0
    current_led_index = 0
    start_time = "2023-09-16T13:03:45.200"
    end_time = "2023-09-16T13:22:35.200"
    # Fetch data for the current time range
    response = urlopen(
        f'https://api.openf1.org/v1/location?session_key=9161&driver_number=81&date>{start_time}&date<{end_time}'
    )
    data = json.loads(response.read().decode('utf-8'))

    if data:
        prev_x = data[0]['x']
        prev_y = data[0]['y']
        for item in data:
            if current_led_index is not None:
                pixels[current_led_index] = (0, 0, 0)  # Turn off the previous LED
            print(item['x'])
            current_x = item['x']
            current_y = item['y']
            distance_traveled += math.sqrt((current_x - prev_x) ** 2 + (current_y - prev_y) ** 2)
            prev_x, prev_y = current_x, current_y
            led_index = ((distance_traveled % total_track_length) / total_track_length) * num_pixels

            print(led_index)
            pixels[math.floor(led_index)] = (255, 0, 0)  # RGB values for green
            current_led_index = math.floor(led_index)
            # Show the updated LED strip
            pixels.show()
            time.sleep(0.001)


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


def fire(cooling, sparking, speed_delay):
    num_pixels = 60
    heat = [0] * num_pixels  # Heat array to track each LED's heat value

    while True:
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

while True:

    #fire(55, 120, 15)
    clock_mode()
    #fetch_and_display_past_session()
    # Comment this line out if you have RGBW/GRBW NeoPixels
    #pixels.fill((255, 0, 255))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((255, 0, 0, 0))
    pixels.show()

    #test_car()
    rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step















