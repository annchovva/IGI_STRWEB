"""
Program Purpose: General utility module for input validation.
Lab4, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import re

def get_string_input(prompt: str) -> str:
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

def get_integer_input(prompt: str, min_value: int = None, max_value: int = None) -> int:
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
        
def get_class_input(prompt: str) -> str:
    """Correct input of the school class."""
    while True:
        try:
            value = input(prompt).strip()

            if not value:
                raise("Class cannot be empty.");
                      
            pattern = r'^([1-9]|10|11)[A-Za-z]$'

            if not re.match(pattern, value):
                raise ValueError("Class must be in format 'Number(1-11)+Letter' (e.g., 10A, 5Б, 11В).")
            
            return value.upper()
        
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nInput interrupted by user. Returning empty string.")
            return ""     
