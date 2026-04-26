"""
Program Purpose: General utility module for input validation.
Lab4, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import re

def get_string_input(prompt):
    """Prompts the user for a string and ensures it is not empty."""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                raise ValueError("Input cannot be empty.")
            return user_input
        except ValueError as e:
            print(f"Error: {e} Please try again.")
        except KeyboardInterrupt:
            print("\nInput interrupted by user. Returning empty string.")
            return ""

def get_integer_input(prompt, min_value= None, max_value= None):
    """Prompts the user for an integer and ensures it is within bounds."""
    while True:
        try:
            user_input = input(prompt).strip()
            value = int(user_input)
            
            if min_value is not None and value < min_value:
                raise ValueError(f"Value must be at least {min_value}.")
            
            if max_value is not None and value > max_value:
                raise ValueError(f"Value must not exceed {max_value}.")
                
            return value
            
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid integer.")
        except KeyboardInterrupt:
            print("\nInput interrupted. Defaulting to 0.")
            return 0
        
def get_float_input(prompt, min_value= None, max_value= None):
    """Prompts the user for an float and ensures it is within bounds."""
    while True:
        try:
            user_input = input(prompt).strip()
            value = float(user_input)
            
            if min_value is not None and value < min_value:
                raise ValueError(f"Value must be at least {min_value}.")
        
            if max_value is not None and value > max_value:                    
                raise ValueError(f"Value must not exceed {max_value}.")
             
            return value
            
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid float.")
        except KeyboardInterrupt:
            print("\nInput interrupted. Defaulting to 0.")
            return 0
            
def get_class_input(prompt):
    """Correct input of the school class."""
    while True:
        try:
            value = input(prompt).strip().upper()

            if not value:
                raise ValueError("Class cannot be empty.")
                      
            pattern = r'^([1-9]|10|11)[A-Z]$'

            if not re.fullmatch(pattern, value):
                raise ValueError("Class must be in format 'Number(1-11)+Letter'.")
            
            return value
        
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nInput interrupted by user. Returning empty string.")
            return ""            

def get_color_input(prompt):
    """Correct input of the color from the list."""

    ALLOWED_COLORS = ['red', 'green', 'blue', 'yellow', 'purple',
                      'orange', 'pink', 'brown', 'black', 'white']

    while True:
        try:
            value = input(prompt).strip().lower()
            if not value:
                raise ValueError("Color cannot be empty.")
            
            if value not in ALLOWED_COLORS:
                raise ValueError(f"Color must be one of: {', '.join(ALLOWED_COLORS)}")
            
            return value

        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nInput interrupted by user. Returning empty string.")
            return "" 
        
def get_optional_int_input(prompt):
    """Read optional integer input."""
    while True:
        value = input(prompt).strip()
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            print("Invalid input. Please enter an integer or press Enter.")        