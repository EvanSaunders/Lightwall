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

def calculate_led_index(distance_traveled, total_track_length, num_pixels):
    return ((distance_traveled % total_track_length) / total_track_length) * num_pixels

def hex_to_rgb(hex_color):
    # If the input is an integer, convert it to a hex string
    if isinstance(hex_color, int):
        hex_color = f"{hex_color:06X}"  # Ensure it's a 6-character string, uppercase

    # Remove '#' if it's included in the hex string (e.g., "#3671C6")
    hex_color = hex_color.lstrip('#')

    # Ensure it's a valid hex color string with 6 characters
    if len(hex_color) != 6 or not all(c in '0123456789ABCDEF' for c in hex_color.upper()):
        raise ValueError("Invalid hex color format")

    # Return a tuple of RGB values by slicing the hex string
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def fetch_and_display_past_session():
    start_time = "2023-09-16T13:03:45.200"
    end_time = "2023-09-16T13:08:35.200"
    current_led_index = 0
    driver_number_list = [1,4,81]
    driver_list = []
    for driver in driver_number_list:


        #get driver team colors
        response = urlopen(f'https://api.openf1.org/v1/drivers?driver_number={driver}&session_key=9161')
        colour_data = json.loads(response.read().decode('utf-8'))
        #print(colour_data)
        #get driver locations for session
        response = urlopen(
        f'https://api.openf1.org/v1/location?session_key=9161&driver_number={driver}&date>{start_time}&date<{end_time}'
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
                print("STILL DRIVER LOCATIONS")
                print(driver.get_led_index())
                if current_led_index is not None:
                    pixels[current_led_index] = (0, 0, 0)
                driver.update_position()
                print(driver.get_driver_colour())
                print(hex_to_rgb(driver.get_driver_colour()))
                print(driver.get_driver_colour())  # Should print a valid hex string or integer
                pixels[driver.get_led_index()] = hex_to_rgb(driver.get_driver_colour())  # RGB values for green
                pixels.show()
                current_led_index = driver.get_led_index()
                all_positions_displayed = False  # Still more positions to display

        if all_positions_displayed:
            break  # Exit the loop if all drivers have no more positions to display

        time.sleep(1)  # Delay for a small amount of time before the next update


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

while False:

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



    fetch_and_display_past_session()
    # Comment this line out if you have RGBW/GRBW NeoPixels
    #pixels.fill((255, 0, 255))
   # Uncomment this line if you have RGBW/GRBW NeoPixels
   # pixels.fill((255, 0, 0, 0))
    pixels.show()
    #time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
    #pixels.fill((0, 255, 0))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 255, 0, 0))
   # pixels.show()
    #time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
    #pixels.fill((0, 0, 255))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 0, 255, 0))
   # pixels.show()
    #time.sleep(1)
    #test_car()
    #rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step
