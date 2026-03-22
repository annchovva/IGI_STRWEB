"""
Purpose: Input validation and data entry
Lab 3, Version 1.1
Author: Gorbachova Anna
Date: 21.03.2026
"""

def get_int(prompt, min_val=None):
    """Safely gets an integer from the user (with optional minimum value)"""
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val <= min_val:
                print(f"Error! Please enter number > {min_val}")
                continue
            return val
        except ValueError:
            print("Invalid input! Please enter number.")

def get_float(prompt, max_val=None):
    """Safely gets a float from the user (with optional maximum value)"""
    while True:
        try:
            val = float(input(prompt))
            if max_val is not None and val > max_val:
                print(f"Error! Plese enter a real number <= {max_val}")
                continue
            return val
        except ValueError:
            print("Invalid input! Please enter a real number.")        