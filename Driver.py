# driver.py

import math
from config import num_pixels, total_track_length

class Driver:
    def __init__(self, driver_number, driver_colour, locations):
        self.driver_number = driver_number
        self.total_distance = 0
        self.current_position = 0
        self.driver_colour = 0
        self.locations = locations
        self.prev_x = 0
        self.prev_y = 0
        if locations:  # Ensure there are locations to avoid indexing errors
            self.starting_x = locations[0][0]  # First x coordinate
            self.starting_y = locations[0][1]  # First y coordinate
            self.prev_x = self.starting_x
            self.prev_y = self.starting_y
        else:
            self.starting_x = 0
            self.starting_y = 0
            self.prev_x = 0
            self.prev_y = 0

    def set_starting_position(self, x_cord, y_cord):
        starting_x = x_cord
        starting_y = y_cord

    def update_position(self):
        if not self.locations:
            return False  # No more locations to process

        current_x, current_y = self.locations.pop(0)

        # Calculate the distance traveled since the last position
        distance = math.sqrt((current_x - self.prev_x) ** 2 + (current_y - self.prev_y) ** 2)
        self.total_distance += distance
        self.prev_x, self.prev_y = current_x, current_y

        # Calculate the LED index based on the distance traveled
        self.current_position = ((self.total_distance % total_track_length) / total_track_length) * num_pixels

        return True

    def get_led_index(self):
        return math.floor(self.current_position)

    def get_driver_colour(self):
        return self.driver_colour

